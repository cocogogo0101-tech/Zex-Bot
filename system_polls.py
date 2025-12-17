"""
system_polls.py - Ultimate Polling System
==========================================
نظام استطلاعات متقدم وشامل

Features:
✅ استطلاعات تفاعلية بأزرار
✅ دعم حتى 10 خيارات
✅ مدة زمنية محددة
✅ نتائج مباشرة ورسوم بيانية
✅ تصويت واحد أو متعدد
✅ إغلاق تلقائي
✅ إحصائيات مفصلة
"""

import discord
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import defaultdict
import json
from logger import bot_logger


class Poll:
    """كائن الاستطلاع"""
    
    def __init__(
        self,
        poll_id: int,
        guild_id: str,
        channel_id: str,
        message_id: str,
        creator_id: str,
        question: str,
        options: List[str],
        duration_minutes: int = 60,
        allow_multiple: bool = False,
        anonymous: bool = False
    ):
        self.poll_id = poll_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.creator_id = creator_id
        self.question = question
        self.options = options
        self.duration_minutes = duration_minutes
        self.allow_multiple = allow_multiple
        self.anonymous = anonymous
        
        self.created_at = datetime.now()
        self.ends_at = self.created_at + timedelta(minutes=duration_minutes)
        self.votes = defaultdict(set)  # {option_index: set(user_ids)}
        self.is_closed = False
    
    def vote(self, user_id: str, option_index: int) -> bool:
        """
        تسجيل صوت
        
        Returns:
            bool: نجح التصويت؟
        """
        if self.is_closed:
            return False
        
        if option_index < 0 or option_index >= len(self.options):
            return False
        
        # إذا لم يكن يسمح بتصويت متعدد، احذف الأصوات السابقة
        if not self.allow_multiple:
            for votes_set in self.votes.values():
                votes_set.discard(user_id)
        
        self.votes[option_index].add(user_id)
        return True
    
    def unvote(self, user_id: str, option_index: int) -> bool:
        """إلغاء صوت"""
        if self.is_closed:
            return False
        
        if option_index in self.votes:
            self.votes[option_index].discard(user_id)
            return True
        
        return False
    
    def get_results(self) -> Dict:
        """
        الحصول على النتائج
        
        Returns:
            dict: النتائج المفصلة
        """
        total_votes = sum(len(voters) for voters in self.votes.values())
        
        results = []
        for i, option in enumerate(self.options):
            vote_count = len(self.votes.get(i, set()))
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            
            results.append({
                'option': option,
                'votes': vote_count,
                'percentage': percentage,
                'voters': list(self.votes.get(i, set())) if not self.anonymous else []
            })
        
        return {
            'total_votes': total_votes,
            'options': results,
            'is_closed': self.is_closed,
            'ends_at': self.ends_at.timestamp()
        }
    
    def has_voted(self, user_id: str) -> bool:
        """التحقق إذا صوّت المستخدم"""
        for voters in self.votes.values():
            if user_id in voters:
                return True
        return False
    
    def get_user_votes(self, user_id: str) -> List[int]:
        """الحصول على خيارات المستخدم"""
        return [i for i, voters in self.votes.items() if user_id in voters]
    
    def close(self):
        """إغلاق الاستطلاع"""
        self.is_closed = True
    
    def is_expired(self) -> bool:
        """التحقق من انتهاء المدة"""
        return datetime.now() >= self.ends_at
    
    def time_remaining(self) -> str:
        """الوقت المتبقي"""
        if self.is_closed:
            return 'مغلق'
        
        if self.is_expired():
            return 'انتهى'
        
        delta = self.ends_at - datetime.now()
        
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f'{hours}h {minutes}m'
        elif minutes > 0:
            return f'{minutes}m {seconds}s'
        else:
            return f'{seconds}s'


class PollSystem:
    """نظام إدارة الاستطلاعات"""
    
    def __init__(self):
        self.polls: Dict[int, Poll] = {}  # {poll_id: Poll}
        self.active_polls: Dict[str, int] = {}  # {message_id: poll_id}
        self.next_poll_id = 1
        self.auto_close_task = None
    
    def start(self, bot: discord.Client):
        """بدء المهام التلقائية"""
        self.bot = bot
        if not self.auto_close_task:
            self.auto_close_task = asyncio.create_task(self._auto_close_polls())
    
    async def create_poll(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel,
        creator: discord.User,
        question: str,
        options: List[str],
        duration_minutes: int = 60,
        allow_multiple: bool = False,
        anonymous: bool = False
    ) -> Optional[Poll]:
        """
        إنشاء استطلاع جديد
        
        Returns:
            Poll أو None
        """
        try:
            # التحقق من عدد الخيارات
            if len(options) < 2:
                return None
            
            if len(options) > 10:
                options = options[:10]
            
            # إنشاء الـ Poll object
            poll_id = self.next_poll_id
            self.next_poll_id += 1
            
            poll = Poll(
                poll_id=poll_id,
                guild_id=str(guild.id),
                channel_id=str(channel.id),
                message_id='',  # سيتم تحديثه لاحقاً
                creator_id=str(creator.id),
                question=question,
                options=options,
                duration_minutes=duration_minutes,
                allow_multiple=allow_multiple,
                anonymous=anonymous
            )
            
            # إنشاء الـ Embed والأزرار
            embed = self._create_poll_embed(poll)
            view = PollView(poll, self)
            
            # إرسال الرسالة
            message = await channel.send(embed=embed, view=view)
            
            # تحديث message_id
            poll.message_id = str(message.id)
            
            # حفظ
            self.polls[poll_id] = poll
            self.active_polls[poll.message_id] = poll_id
            
            bot_logger.info(
                f'استطلاع جديد #{poll_id} في {guild.name}: {question}'
            )
            
            return poll
        
        except Exception as e:
            bot_logger.exception('خطأ في create_poll', e)
            return None
    
    def _create_poll_embed(self, poll: Poll) -> discord.Embed:
        """إنشاء embed الاستطلاع"""
        results = poll.get_results()
        total = results['total_votes']
        
        embed = discord.Embed(
            title='📊 ' + poll.question,
            color=discord.Color.blue() if not poll.is_closed else discord.Color.green(),
            timestamp=poll.created_at
        )
        
        # الخيارات والنتائج
        for i, option_data in enumerate(results['options']):
            option = option_data['option']
            votes = option_data['votes']
            percentage = option_data['percentage']
            
            # شريط التقدم
            bar_length = 20
            filled = int((percentage / 100) * bar_length) if total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            
            emoji = self._get_emoji(i)
            
            value = f'{emoji} {bar} **{votes}** ({percentage:.1f}%)'
            
            embed.add_field(
                name=option,
                value=value,
                inline=False
            )
        
        # المعلومات السفلية
        info_parts = [
            f'👥 **إجمالي الأصوات:** {total}',
        ]
        
        if poll.allow_multiple:
            info_parts.append('📌 يمكن اختيار عدة خيارات')
        
        if poll.anonymous:
            info_parts.append('🔒 تصويت سري')
        
        if not poll.is_closed:
            time_left = poll.time_remaining()
            info_parts.append(f'⏰ ينتهي في: **{time_left}**')
        else:
            info_parts.append('✅ **مغلق**')
        
        embed.description = '\n'.join(info_parts)
        
        embed.set_footer(
            text=f'ID: {poll.poll_id} • بواسطة {poll.creator_id}',
            icon_url=None
        )
        
        return embed
    
    def _get_emoji(self, index: int) -> str:
        """الحصول على emoji حسب الرقم"""
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        return emojis[index] if index < len(emojis) else '❓'
    
    async def update_poll_message(self, poll: Poll):
        """تحديث رسالة الاستطلاع"""
        try:
            guild = self.bot.get_guild(int(poll.guild_id))
            if not guild:
                return
            
            channel = guild.get_channel(int(poll.channel_id))
            if not channel:
                return
            
            message = await channel.fetch_message(int(poll.message_id))
            if not message:
                return
            
            embed = self._create_poll_embed(poll)
            view = PollView(poll, self) if not poll.is_closed else None
            
            await message.edit(embed=embed, view=view)
        
        except Exception as e:
            bot_logger.error(f'خطأ في update_poll_message: {e}')
    
    async def close_poll(self, poll_id: int, closer: Optional[discord.User] = None) -> bool:
        """
        إغلاق استطلاع
        
        Returns:
            bool: نجح الإغلاق؟
        """
        if poll_id not in self.polls:
            return False
        
        poll = self.polls[poll_id]
        
        if poll.is_closed:
            return False
        
        poll.close()
        
        # تحديث الرسالة
        await self.update_poll_message(poll)
        
        # إرسال النتائج النهائية
        try:
            guild = self.bot.get_guild(int(poll.guild_id))
            channel = guild.get_channel(int(poll.channel_id))
            
            results_embed = self._create_results_embed(poll)
            await channel.send(embed=results_embed)
        except:
            pass
        
        reason = f'بواسطة {closer.name}' if closer else 'تلقائياً (انتهاء المدة)'
        bot_logger.info(f'تم إغلاق استطلاع #{poll_id} - {reason}')
        
        return True
    
    def _create_results_embed(self, poll: Poll) -> discord.Embed:
        """embed النتائج النهائية"""
        results = poll.get_results()
        total = results['total_votes']
        
        embed = discord.Embed(
            title='📊 النتائج النهائية',
            description=f'**{poll.question}**',
            color=discord.Color.green()
        )
        
        # ترتيب الخيارات حسب الأصوات
        sorted_options = sorted(
            enumerate(results['options']),
            key=lambda x: x[1]['votes'],
            reverse=True
        )
        
        for rank, (i, option_data) in enumerate(sorted_options, 1):
            option = option_data['option']
            votes = option_data['votes']
            percentage = option_data['percentage']
            
            medal = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else f'{rank}.'
            
            embed.add_field(
                name=f'{medal} {option}',
                value=f'**{votes}** أصوات ({percentage:.1f}%)',
                inline=False
            )
        
        embed.add_field(
            name='📊 الإحصائيات',
            value=(
                f'**إجمالي الأصوات:** {total}\n'
                f'**المدة:** {poll.duration_minutes} دقيقة\n'
                f'**الحالة:** مغلق ✅'
            ),
            inline=False
        )
        
        embed.set_footer(text=f'الاستطلاع #{poll.poll_id}')
        
        return embed
    
    async def _auto_close_polls(self):
        """مهمة إغلاق الاستطلاعات التلقائية"""
        while True:
            try:
                await asyncio.sleep(30)  # كل 30 ثانية
                
                now = datetime.now()
                
                for poll_id, poll in list(self.polls.items()):
                    if not poll.is_closed and poll.is_expired():
                        await self.close_poll(poll_id)
                
            except Exception as e:
                bot_logger.error(f'خطأ في _auto_close_polls: {e}')
    
    def get_poll(self, poll_id: int) -> Optional[Poll]:
        """الحصول على استطلاع"""
        return self.polls.get(poll_id)
    
    def get_poll_by_message(self, message_id: str) -> Optional[Poll]:
        """الحصول على استطلاع من message_id"""
        poll_id = self.active_polls.get(message_id)
        if poll_id:
            return self.polls.get(poll_id)
        return None


class PollView(discord.ui.View):
    """أزرار الاستطلاع"""
    
    def __init__(self, poll: Poll, poll_system: PollSystem):
        super().__init__(timeout=None)
        self.poll = poll
        self.poll_system = poll_system
        
        # إنشاء أزرار للخيارات
        for i, option in enumerate(poll.options):
            button = PollButton(i, option, self.poll_system._get_emoji(i))
            self.add_item(button)


class PollButton(discord.ui.Button):
    """زر خيار الاستطلاع"""
    
    def __init__(self, option_index: int, label: str, emoji: str):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=label[:80],  # Discord limit
            emoji=emoji,
            custom_id=f'poll_{option_index}'
        )
        self.option_index = option_index
    
    async def callback(self, interaction: discord.Interaction):
        """عند الضغط على الزر"""
        try:
            # الحصول على الاستطلاع
            view: PollView = self.view
            poll = view.poll
            
            if poll.is_closed:
                await interaction.response.send_message(
                    '⚠️ هذا الاستطلاع مغلق',
                    ephemeral=True
                )
                return
            
            user_id = str(interaction.user.id)
            
            # التحقق إذا كان قد صوّت على هذا الخيار
            if user_id in poll.votes.get(self.option_index, set()):
                # إلغاء الصوت
                poll.unvote(user_id, self.option_index)
                message = f'تم إلغاء صوتك على: **{poll.options[self.option_index]}**'
            else:
                # تسجيل الصوت
                success = poll.vote(user_id, self.option_index)
                
                if success:
                    message = f'✅ تم تسجيل صوتك على: **{poll.options[self.option_index]}**'
                else:
                    message = '❌ فشل تسجيل الصوت'
            
            # تحديث الرسالة
            await view.poll_system.update_poll_message(poll)
            
            await interaction.response.send_message(message, ephemeral=True)
        
        except Exception as e:
            bot_logger.exception('خطأ في PollButton callback', e)
            await interaction.response.send_message(
                '❌ حدث خطأ',
                ephemeral=True
            )


# النسخة العامة
poll_system = PollSystem()
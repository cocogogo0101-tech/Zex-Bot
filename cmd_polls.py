"""
cmd_polls.py - Poll Commands
=============================
أوامر الاستطلاعات المتقدمة
"""

import discord
from discord import app_commands
from discord.ext import commands
from system_polls import poll_system
import permissions, embeds
from logger import bot_logger
from typing import Optional


def setup_poll_commands(bot: commands.Bot):
    """تسجيل أوامر الاستطلاعات"""
    
    poll_group = app_commands.Group(
        name='poll',
        description='إدارة الاستطلاعات التفاعلية'
    )
    
    # ==================== إنشاء استطلاع ====================
    
    @poll_group.command(name='create', description='إنشاء استطلاع جديد')
    @app_commands.describe(
        question='السؤال أو العنوان',
        options='الخيارات مفصولة بـ | (مثال: نعم|لا|ربما)',
        duration='المدة بالدقائق (افتراضي: 60)',
        multiple='السماح بتصويت متعدد (افتراضي: لا)',
        anonymous='تصويت سري (افتراضي: لا)'
    )
    @permissions.is_moderator()
    async def create_poll(
        interaction: discord.Interaction,
        question: str,
        options: str,
        duration: int = 60,
        multiple: bool = False,
        anonymous: bool = False
    ):
        """إنشاء استطلاع"""
        try:
            # التحقق من المدة
            if duration < 1 or duration > 10080:  # أسبوع كحد أقصى
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        'المدة يجب أن تكون بين 1 دقيقة و 10080 دقيقة (أسبوع)'
                    ),
                    ephemeral=True
                )
                return
            
            # تقسيم الخيارات
            option_list = [opt.strip() for opt in options.split('|') if opt.strip()]
            
            if len(option_list) < 2:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        'يجب إضافة خيارين على الأقل\n**مثال:** `نعم|لا|ربما`'
                    ),
                    ephemeral=True
                )
                return
            
            if len(option_list) > 10:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'تحذير',
                        f'تم اختيار أول 10 خيارات فقط من {len(option_list)}'
                    ),
                    ephemeral=True
                )
                option_list = option_list[:10]
            
            # إنشاء الاستطلاع
            poll = await poll_system.create_poll(
                guild=interaction.guild,
                channel=interaction.channel,
                creator=interaction.user,
                question=question,
                options=option_list,
                duration_minutes=duration,
                allow_multiple=multiple,
                anonymous=anonymous
            )
            
            if poll:
                embed = discord.Embed(
                    title='✅ تم إنشاء الاستطلاع',
                    color=discord.Color.green()
                )
                embed.add_field(name='السؤال', value=question, inline=False)
                embed.add_field(name='الخيارات', value=f'{len(option_list)} خيارات', inline=True)
                embed.add_field(name='المدة', value=f'{duration} دقيقة', inline=True)
                embed.add_field(name='ID', value=f'`{poll.poll_id}`', inline=True)
                
                if multiple:
                    embed.add_field(name='ملاحظة', value='✅ يمكن اختيار عدة خيارات', inline=False)
                
                if anonymous:
                    embed.add_field(name='ملاحظة', value='🔒 التصويت سري', inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                bot_logger.info(
                    f'استطلاع جديد #{poll.poll_id} في {interaction.guild.name} '
                    f'بواسطة {interaction.user.name}'
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'فشل إنشاء الاستطلاع'),
                    ephemeral=True
                )
        
        except Exception as e:
            bot_logger.exception('خطأ في create_poll', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== استطلاع سريع ====================
    
    @poll_group.command(name='quick', description='استطلاع سريع بنعم/لا')
    @app_commands.describe(
        question='السؤال',
        duration='المدة بالدقائق (افتراضي: 5)'
    )
    @permissions.is_moderator()
    async def quick_poll(
        interaction: discord.Interaction,
        question: str,
        duration: int = 5
    ):
        """استطلاع سريع"""
        try:
            poll = await poll_system.create_poll(
                guild=interaction.guild,
                channel=interaction.channel,
                creator=interaction.user,
                question=question,
                options=['نعم ✅', 'لا ❌'],
                duration_minutes=duration,
                allow_multiple=False,
                anonymous=False
            )
            
            if poll:
                await interaction.response.send_message(
                    embed=embeds.success_embed(
                        'تم',
                        f'تم إنشاء استطلاع سريع (ID: `{poll.poll_id}`)'
                    ),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'فشل إنشاء الاستطلاع'),
                    ephemeral=True
                )
        
        except Exception as e:
            bot_logger.exception('خطأ في quick_poll', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== إغلاق استطلاع ====================
    
    @poll_group.command(name='close', description='إغلاق استطلاع مبكراً')
    @app_commands.describe(poll_id='معرف الاستطلاع')
    @permissions.is_moderator()
    async def close_poll(interaction: discord.Interaction, poll_id: int):
        """إغلاق استطلاع"""
        try:
            poll = poll_system.get_poll(poll_id)
            
            if not poll:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        f'لم يتم العثور على استطلاع بـ ID: {poll_id}'
                    ),
                    ephemeral=True
                )
                return
            
            # التحقق من الصلاحيات
            if str(interaction.user.id) != poll.creator_id:
                if not await permissions.check_permissions(interaction.user, administrator=True):
                    await interaction.response.send_message(
                        embed=embeds.error_embed(
                            'خطأ',
                            'يمكن فقط منشئ الاستطلاع أو المشرفين إغلاقه'
                        ),
                        ephemeral=True
                    )
                    return
            
            if poll.is_closed:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'تنبيه',
                        'هذا الاستطلاع مغلق بالفعل'
                    ),
                    ephemeral=True
                )
                return
            
            # إغلاق
            success = await poll_system.close_poll(poll_id, interaction.user)
            
            if success:
                await interaction.response.send_message(
                    embed=embeds.success_embed(
                        'تم',
                        f'تم إغلاق الاستطلاع #{poll_id}'
                    )
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'فشل إغلاق الاستطلاع'),
                    ephemeral=True
                )
        
        except Exception as e:
            bot_logger.exception('خطأ في close_poll', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== عرض النتائج ====================
    
    @poll_group.command(name='results', description='عرض نتائج استطلاع')
    @app_commands.describe(poll_id='معرف الاستطلاع')
    async def poll_results(interaction: discord.Interaction, poll_id: int):
        """عرض النتائج"""
        try:
            poll = poll_system.get_poll(poll_id)
            
            if not poll:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        f'لم يتم العثور على استطلاع بـ ID: {poll_id}'
                    ),
                    ephemeral=True
                )
                return
            
            results = poll.get_results()
            total = results['total_votes']
            
            embed = discord.Embed(
                title=f'📊 نتائج الاستطلاع #{poll_id}',
                description=f'**{poll.question}**',
                color=discord.Color.blue() if not poll.is_closed else discord.Color.green()
            )
            
            # الخيارات مرتبة
            sorted_options = sorted(
                enumerate(results['options']),
                key=lambda x: x[1]['votes'],
                reverse=True
            )
            
            for rank, (i, option_data) in enumerate(sorted_options, 1):
                option = option_data['option']
                votes = option_data['votes']
                percentage = option_data['percentage']
                
                # شريط التقدم
                bar_length = 15
                filled = int((percentage / 100) * bar_length) if total > 0 else 0
                bar = '█' * filled + '░' * (bar_length - filled)
                
                medal = '🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else f'#{rank}'
                
                embed.add_field(
                    name=f'{medal} {option}',
                    value=f'{bar} **{votes}** ({percentage:.1f}%)',
                    inline=False
                )
            
            # معلومات إضافية
            info = [
                f'**إجمالي الأصوات:** {total}',
                f'**الحالة:** {"✅ مغلق" if poll.is_closed else "🔄 نشط"}',
            ]
            
            if not poll.is_closed:
                info.append(f'**ينتهي في:** {poll.time_remaining()}')
            
            embed.add_field(
                name='📊 المعلومات',
                value='\n'.join(info),
                inline=False
            )
            
            embed.set_footer(text=f'تم الإنشاء بواسطة: {poll.creator_id}')
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في poll_results', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== صوتي ====================
    
    @poll_group.command(name='myvote', description='عرض صوتك في استطلاع')
    @app_commands.describe(poll_id='معرف الاستطلاع')
    async def my_vote(interaction: discord.Interaction, poll_id: int):
        """عرض صوت المستخدم"""
        try:
            poll = poll_system.get_poll(poll_id)
            
            if not poll:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        f'لم يتم العثور على استطلاع بـ ID: {poll_id}'
                    ),
                    ephemeral=True
                )
                return
            
            user_id = str(interaction.user.id)
            
            if not poll.has_voted(user_id):
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لم تصوّت',
                        f'لم تصوّت في الاستطلاع #{poll_id} بعد'
                    ),
                    ephemeral=True
                )
                return
            
            votes = poll.get_user_votes(user_id)
            
            embed = discord.Embed(
                title=f'🗳️ صوتك في الاستطلاع #{poll_id}',
                description=f'**{poll.question}**',
                color=discord.Color.green()
            )
            
            for vote_index in votes:
                option = poll.options[vote_index]
                embed.add_field(
                    name='اخترت',
                    value=f'✅ **{option}**',
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            bot_logger.exception('خطأ في my_vote', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    bot.tree.add_command(poll_group)
    bot_logger.success('✅ تم تسجيل أوامر الاستطلاعات')
"""
cmd_analytics.py - Simple Analytics
====================================
إحصائيات بسيطة للسيرفر
"""

import discord
from discord import app_commands
from discord.ext import commands
from database import db
from system_leveling import leveling_system
import permissions, embeds
from logger import bot_logger
from datetime import datetime, timedelta


def setup_analytics_commands(bot: commands.Bot):
    """تسجيل أوامر الإحصائيات"""
    
    @bot.tree.command(name='analytics', description='إحصائيات السيرفر')
    @app_commands.describe(days='عدد الأيام (افتراضي: 7)')
    @permissions.is_moderator()
    async def analytics(interaction: discord.Interaction, days: int = 7):
        """إحصائيات السيرفر"""
        try:
            if days < 1 or days > 90:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'عدد الأيام يجب أن يكون بين 1-90'),
                    ephemeral=True
                )
                return
            
            await interaction.response.defer()
            
            guild_id = str(interaction.guild.id)
            
            # جلب الإحصائيات
            stats = await db.get_stats(guild_id, days=days)
            
            if not stats:
                await interaction.followup.send(
                    embed=embeds.warning_embed(
                        'لا توجد بيانات',
                        'لا توجد إحصائيات كافية بعد'
                    )
                )
                return
            
            # حساب الإجماليات
            total_messages = sum(s.get('messages', 0) for s in stats)
            total_joins = sum(s.get('joins', 0) for s in stats)
            total_leaves = sum(s.get('leaves', 0) for s in stats)
            total_voice_minutes = sum(s.get('voice_minutes', 0) for s in stats)
            
            # معلومات السيرفر
            guild = interaction.guild
            
            embed = discord.Embed(
                title=f'📊 إحصائيات {guild.name}',
                description=f'آخر {days} أيام',
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # الأعضاء
            total_members = guild.member_count
            humans = sum(1 for m in guild.members if not m.bot)
            bots = sum(1 for m in guild.members if m.bot)
            online = sum(1 for m in guild.members if m.status != discord.Status.offline)
            
            embed.add_field(
                name='👥 الأعضاء',
                value=(
                    f'**الإجمالي:** {total_members:,}\n'
                    f'👤 **بشر:** {humans:,}\n'
                    f'🤖 **بوتات:** {bots}\n'
                    f'🟢 **متصل:** {online:,}'
                ),
                inline=True
            )
            
            # القنوات
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            
            embed.add_field(
                name='📁 القنوات',
                value=(
                    f'💬 **نصية:** {text_channels}\n'
                    f'🔊 **صوتية:** {voice_channels}'
                ),
                inline=True
            )
            
            # النشاط
            avg_messages = total_messages / days if days > 0 else 0
            
            embed.add_field(
                name='📈 النشاط',
                value=(
                    f'**الرسائل:** {total_messages:,}\n'
                    f'**متوسط/يوم:** {avg_messages:.1f}\n'
                    f'**الوقت الصوتي:** {total_voice_minutes:,}m'
                ),
                inline=True
            )
            
            # الانضمامات والمغادرات
            net_change = total_joins - total_leaves
            net_emoji = '📈' if net_change > 0 else '📉' if net_change < 0 else '➡️'
            
            embed.add_field(
                name='📥 الانضمامات',
                value=(
                    f'**انضموا:** {total_joins}\n'
                    f'**غادروا:** {total_leaves}\n'
                    f'**الصافي:** {net_emoji} {net_change:+d}'
                ),
                inline=True
            )
            
            # إحصائيات المستويات
            try:
                level_stats = await leveling_system.get_guild_stats(guild_id)
                
                if level_stats and level_stats.get('total_users', 0) > 0:
                    embed.add_field(
                        name='🎮 المستويات',
                        value=(
                            f'**المستخدمون:** {level_stats["total_users"]}\n'
                            f'**إجمالي XP:** {level_stats["total_xp"]:,}\n'
                            f'**متوسط المستوى:** {level_stats["avg_level"]:.1f}\n'
                            f'**أعلى مستوى:** {level_stats["max_level"]}'
                        ),
                        inline=True
                    )
            except:
                pass
            
            # Boost
            if guild.premium_subscription_count:
                embed.add_field(
                    name='💎 Boost',
                    value=(
                        f'**المستوى:** {guild.premium_tier}\n'
                        f'**العدد:** {guild.premium_subscription_count}'
                    ),
                    inline=True
                )
            
            # الرسم البياني (بسيط)
            if len(stats) >= 3:
                # آخر 7 أيام
                recent_stats = stats[-7:] if len(stats) >= 7 else stats
                
                # رسم بياني نصي بسيط للرسائل
                max_messages = max((s.get('messages', 0) for s in recent_stats), default=1)
                
                chart_lines = []
                for s in recent_stats:
                    date = s.get('date', '')
                    messages = s.get('messages', 0)
                    
                    # شريط بسيط
                    bar_length = 15
                    filled = int((messages / max_messages) * bar_length) if max_messages > 0 else 0
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    chart_lines.append(f'`{date[-5:]}` {bar} {messages}')
                
                embed.add_field(
                    name='📊 الرسائل (آخر 7 أيام)',
                    value='\n'.join(chart_lines),
                    inline=False
                )
            
            embed.set_footer(
                text=f'مطلوب بواسطة {interaction.user.name}',
                icon_url=interaction.user.display_avatar.url
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في analytics', e)
            await interaction.followup.send(
                embed=embeds.error_embed('خطأ', str(e))
            )
    
    @bot.tree.command(name='topusers', description='أكثر الأعضاء نشاطاً')
    @app_commands.describe(limit='عدد الأعضاء (افتراضي: 10)')
    async def top_users(interaction: discord.Interaction, limit: int = 10):
        """أكثر الأعضاء نشاطاً"""
        try:
            limit = max(1, min(limit, 25))
            
            # جلب من نظام المستويات
            leaderboard = await leveling_system.get_leaderboard(
                str(interaction.guild.id),
                limit=limit
            )
            
            if not leaderboard:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لا توجد بيانات',
                        'لا توجد بيانات نشاط بعد'
                    ),
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title='🏆 أكثر الأعضاء نشاطاً',
                description=f'أعلى {len(leaderboard)} أعضاء',
                color=discord.Color.gold()
            )
            
            medals = ['🥇', '🥈', '🥉']
            
            for i, entry in enumerate(leaderboard, 1):
                user_id = entry['user_id']
                messages = entry.get('messages', 0)
                level = entry.get('level', 0)
                
                medal = medals[i-1] if i <= 3 else f'`#{i}`'
                
                embed.add_field(
                    name=f'{medal} <@{user_id}>',
                    value=f'المستوى {level} • {messages:,} رسالة',
                    inline=False
                )
            
            embed.set_footer(
                text=f'مطلوب بواسطة {interaction.user.name}',
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في top_users', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    bot_logger.success('✅ تم تسجيل أوامر الإحصائيات')
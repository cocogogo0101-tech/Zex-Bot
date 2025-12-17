"""
cmd_invites.py - Invite Tracking Commands
==========================================
أوامر تتبع الدعوات والمكافآت
"""

import discord
from discord import app_commands
from discord.ext import commands
from system_invites import invite_tracker, invite_rewards
import permissions, embeds
from logger import bot_logger
from typing import Optional


def setup_invite_commands(bot: commands.Bot):
    """تسجيل أوامر الدعوات"""
    
    invite_group = app_commands.Group(
        name='invites',
        description='نظام تتبع الدعوات والمكافآت'
    )
    
    # ==================== عرض دعوات عضو ====================
    
    @invite_group.command(name='check', description='عرض عدد دعوات عضو')
    @app_commands.describe(user='العضو (افتراضي: أنت)')
    async def check_invites(
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """عرض عدد الدعوات"""
        try:
            user = user or interaction.user
            
            # جلب عدد الدعوات
            invite_count = await invite_tracker.get_user_invites(
                str(interaction.guild.id),
                str(user.id)
            )
            
            embed = discord.Embed(
                title=f'📨 دعوات {user.name}',
                color=discord.Color.blue()
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            embed.add_field(
                name='إجمالي الدعوات الناجحة',
                value=f'## **{invite_count}** شخص',
                inline=False
            )
            
            # التحقق من المكافأة التالية
            next_reward = await invite_rewards.get_next_reward(
                str(interaction.guild.id),
                invite_count
            )
            
            if next_reward:
                role = interaction.guild.get_role(int(next_reward['role_id']))
                if role:
                    remaining = next_reward['required_invites'] - invite_count
                    embed.add_field(
                        name='🎁 المكافأة التالية',
                        value=(
                            f'**{remaining}** دعوات إضافية\n'
                            f'للحصول على دور {role.mention}'
                        ),
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في check_invites', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== لوحة صدارة الدعوات ====================
    
    @invite_group.command(name='leaderboard', description='لوحة صدارة الدعوات')
    @app_commands.describe(limit='عدد الأعضاء (افتراضي: 10)')
    async def invites_leaderboard(
        interaction: discord.Interaction,
        limit: int = 10
    ):
        """لوحة الصدارة"""
        try:
            limit = max(1, min(limit, 25))  # بين 1-25
            
            leaderboard = await invite_tracker.get_invite_leaderboard(
                str(interaction.guild.id),
                limit=limit
            )
            
            if not leaderboard:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لا توجد بيانات',
                        'لا توجد دعوات مسجلة بعد'
                    ),
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title='🏆 لوحة صدارة الدعوات',
                description=f'أعلى {len(leaderboard)} مدعوين في السيرفر',
                color=discord.Color.gold()
            )
            
            medals = ['🥇', '🥈', '🥉']
            
            for i, entry in enumerate(leaderboard, 1):
                user_id = entry['user_id']
                invites = entry['invites']
                
                medal = medals[i-1] if i <= 3 else f'`#{i}`'
                
                embed.add_field(
                    name=f'{medal} <@{user_id}>',
                    value=f'**{invites}** دعوات ناجحة',
                    inline=False
                )
            
            embed.set_footer(
                text=f'مطلوب بواسطة {interaction.user.name}',
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في invites_leaderboard', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== من دعا عضو ====================
    
    @invite_group.command(name='whoinvited', description='معرفة من دعا عضواً معيناً')
    @app_commands.describe(user='العضو')
    async def who_invited(
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """من دعا هذا العضو؟"""
        try:
            inviter_id = await invite_tracker.get_invited_by(
                str(interaction.guild.id),
                str(user.id)
            )
            
            if not inviter_id:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'غير معروف',
                        f'لا توجد معلومات عن من دعا {user.mention}'
                    ),
                    ephemeral=True
                )
                return
            
            inviter = interaction.guild.get_member(int(inviter_id))
            
            embed = discord.Embed(
                title='📨 معلومات الدعوة',
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name='العضو',
                value=user.mention,
                inline=True
            )
            
            if inviter:
                embed.add_field(
                    name='تمت دعوته بواسطة',
                    value=inviter.mention,
                    inline=True
                )
                embed.set_thumbnail(url=inviter.display_avatar.url)
            else:
                embed.add_field(
                    name='تمت دعوته بواسطة',
                    value=f'<@{inviter_id}> (غادر السيرفر)',
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في who_invited', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== إدارة المكافآت ====================
    
    rewards_group = app_commands.Group(
        name='inviterewards',
        description='إدارة مكافآت الدعوات',
        parent=invite_group
    )
    
    @rewards_group.command(name='add', description='إضافة مكافأة دعوات')
    @app_commands.describe(
        invites='عدد الدعوات المطلوب',
        role='الدور الذي سيحصل عليه'
    )
    @permissions.is_admin()
    async def add_reward(
        interaction: discord.Interaction,
        invites: int,
        role: discord.Role
    ):
        """إضافة مكافأة"""
        try:
            if invites < 1:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'عدد الدعوات يجب أن يكون 1 أو أكثر'),
                    ephemeral=True
                )
                return
            
            # التحقق من الدور
            if role >= interaction.guild.me.top_role:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        'لا يمكنني إعطاء هذا الدور (رتبته أعلى أو مساوية لرتبتي)'
                    ),
                    ephemeral=True
                )
                return
            
            if role.managed:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        'هذا الدور يُدار بواسطة تطبيق أو بوت'
                    ),
                    ephemeral=True
                )
                return
            
            await invite_rewards.add_reward(
                str(interaction.guild.id),
                invites,
                str(role.id)
            )
            
            embed = embeds.success_embed(
                'تم إضافة المكافأة',
                f'عند الوصول لـ **{invites}** دعوة، سيحصل العضو على دور {role.mention}'
            )
            
            await interaction.response.send_message(embed=embed)
            
            bot_logger.info(
                f'مكافأة دعوات جديدة في {interaction.guild.name}: '
                f'{invites} -> {role.name}'
            )
        
        except Exception as e:
            bot_logger.exception('خطأ في add_reward', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    @rewards_group.command(name='remove', description='حذف مكافأة دعوات')
    @app_commands.describe(invites='عدد الدعوات')
    @permissions.is_admin()
    async def remove_reward(interaction: discord.Interaction, invites: int):
        """حذف مكافأة"""
        try:
            await invite_rewards.remove_reward(
                str(interaction.guild.id),
                invites
            )
            
            await interaction.response.send_message(
                embed=embeds.success_embed(
                    'تم',
                    f'تم حذف مكافأة الـ {invites} دعوة'
                )
            )
        
        except Exception as e:
            bot_logger.exception('خطأ في remove_reward', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    @rewards_group.command(name='list', description='عرض جميع مكافآت الدعوات')
    async def list_rewards(interaction: discord.Interaction):
        """عرض المكافآت"""
        try:
            rewards = await invite_rewards.get_rewards(str(interaction.guild.id))
            
            if not rewards:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لا توجد مكافآت',
                        'لم يتم إضافة أي مكافآت بعد\n\n'
                        'استخدم `/invites inviterewards add` لإضافة مكافأة'
                    ),
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title='🎁 مكافآت الدعوات',
                description='المكافآت المتاحة في السيرفر',
                color=discord.Color.gold()
            )
            
            for reward in sorted(rewards, key=lambda r: r['required_invites']):
                invites_needed = reward['required_invites']
                role = interaction.guild.get_role(int(reward['role_id']))
                
                if role:
                    embed.add_field(
                        name=f'📨 {invites_needed} دعوات',
                        value=f'الدور: {role.mention}',
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            bot_logger.exception('خطأ في list_rewards', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    bot.tree.add_command(invite_group)
    bot_logger.success('✅ تم تسجيل أوامر الدعوات')
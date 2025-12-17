"""
cmd_autoresponse.py - Ultimate Version
=======================================
أوامر الردود التلقائية الشاملة والمتقدمة

Features:
✅ إضافة/حذف/تعديل ردود
✅ أنواع مطابقة متعددة
✅ قوالب جاهزة
✅ Cooldowns + Chance
✅ تخصيص متقدم
✅ إحصائيات
"""

import discord
from discord import app_commands
from discord.ext import commands
from system_autoresponse import autoresponse_system
import permissions, embeds
from logger import bot_logger
from typing import Optional


def setup_autoresponse_commands(bot: commands.Bot):
    """تسجيل أوامر الردود التلقائية"""
    
    ar_group = app_commands.Group(
        name='autoresponse',
        description='إدارة الردود التلقائية الذكية'
    )
    
    # ==================== إضافة رد بسيط ====================
    
    @ar_group.command(name='add', description='إضافة رد تلقائي جديد')
    @app_commands.describe(
        trigger='الكلمة/النص المحفز (مثال: سلام عليكم)',
        response='الرد (مثال: وعليكم السلام)',
        type='نوع المطابقة'
    )
    @app_commands.choices(type=[
        app_commands.Choice(name='يحتوي على (contains) - الافتراضي', value='contains'),
        app_commands.Choice(name='مطابقة تامة (exact)', value='exact'),
        app_commands.Choice(name='يبدأ بـ (startswith)', value='startswith'),
        app_commands.Choice(name='ينتهي بـ (endswith)', value='endswith'),
    ])
    @permissions.is_admin()
    async def add_response(
        interaction: discord.Interaction,
        trigger: str,
        response: str,
        type: str = 'contains'
    ):
        """إضافة رد تلقائي"""
        try:
            response_id = await autoresponse_system.add_response(
                str(interaction.guild.id),
                trigger,
                response,
                type
            )
            
            if response_id:
                embed = discord.Embed(
                    title='✅ تم إضافة الرد التلقائي',
                    color=discord.Color.green()
                )
                embed.add_field(name='المحفز', value=f'`{trigger}`', inline=True)
                embed.add_field(name='النوع', value=type, inline=True)
                embed.add_field(name='ID', value=f'`{response_id}`', inline=True)
                embed.add_field(name='الرد', value=response, inline=False)
                
                embed.add_field(
                    name='💡 نصيحة',
                    value=(
                        'يمكنك استخدام متغيرات:\n'
                        '• `{mention}` - منشن العضو\n'
                        '• `{user}` - اسم العضو\n'
                        '• `{server}` - اسم السيرفر\n'
                        '• `{membercount}` - عدد الأعضاء'
                    ),
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                
                bot_logger.info(
                    f'رد تلقائي جديد في {interaction.guild.name}: '
                    f'{trigger} -> {response}'
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'فشل إضافة الرد التلقائي'),
                    ephemeral=True
                )
                
        except Exception as e:
            bot_logger.exception('خطأ في add_response', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', f'حدث خطأ: {str(e)}'),
                ephemeral=True
            )
    
    # ==================== إضافة متقدم ====================
    
    @ar_group.command(name='addadvanced', description='إضافة رد تلقائي بإعدادات متقدمة')
    @app_commands.describe(
        trigger='الكلمة المحفزة',
        response='الرد',
        type='نوع المطابقة',
        chance='احتمالية الرد (0-100)',
        cooldown='وقت الانتظار بالثواني'
    )
    @app_commands.choices(type=[
        app_commands.Choice(name='يحتوي على', value='contains'),
        app_commands.Choice(name='مطابقة تامة', value='exact'),
        app_commands.Choice(name='يبدأ بـ', value='startswith'),
        app_commands.Choice(name='ينتهي بـ', value='endswith'),
        app_commands.Choice(name='Regex (متقدم)', value='regex'),
    ])
    @permissions.is_admin()
    async def add_advanced(
        interaction: discord.Interaction,
        trigger: str,
        response: str,
        type: str = 'contains',
        chance: int = 100,
        cooldown: int = 0
    ):
        """إضافة رد متقدم"""
        try:
            # التحقق من المدخلات
            if chance < 0 or chance > 100:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'الاحتمالية يجب أن تكون بين 0-100'),
                    ephemeral=True
                )
                return
            
            if cooldown < 0:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'الانتظار لا يمكن أن يكون سالباً'),
                    ephemeral=True
                )
                return
            
            response_id = await autoresponse_system.add_response(
                str(interaction.guild.id),
                trigger,
                response,
                type,
                chance,
                cooldown
            )
            
            if response_id:
                embed = discord.Embed(
                    title='✅ تم إضافة الرد المتقدم',
                    color=discord.Color.green()
                )
                embed.add_field(name='المحفز', value=f'`{trigger}`', inline=True)
                embed.add_field(name='النوع', value=type, inline=True)
                embed.add_field(name='ID', value=f'`{response_id}`', inline=True)
                embed.add_field(name='الرد', value=response, inline=False)
                embed.add_field(name='الاحتمالية', value=f'{chance}%', inline=True)
                embed.add_field(name='الانتظار', value=f'{cooldown}s', inline=True)
                
                await interaction.response.send_message(embed=embed)
                
                bot_logger.info(
                    f'رد متقدم في {interaction.guild.name}: '
                    f'{trigger} (chance={chance}%, cooldown={cooldown}s)'
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'فشل إضافة الرد'),
                    ephemeral=True
                )
                
        except Exception as e:
            bot_logger.exception('خطأ في add_advanced', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== عرض الردود ====================
    
    @ar_group.command(name='list', description='عرض جميع الردود التلقائية')
    @app_commands.describe(page='رقم الصفحة')
    async def list_responses(
        interaction: discord.Interaction,
        page: int = 1
    ):
        """عرض قائمة الردود"""
        try:
            responses = await autoresponse_system.get_responses(str(interaction.guild.id))
            
            if not responses:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لا توجد ردود',
                        'لم يتم إضافة أي ردود تلقائية بعد\n\n'
                        'استخدم `/autoresponse add` لإضافة رد'
                    ),
                    ephemeral=True
                )
                return
            
            # Pagination
            per_page = 5
            total_pages = (len(responses) - 1) // per_page + 1
            page = max(1, min(page, total_pages))
            
            start = (page - 1) * per_page
            end = start + per_page
            page_responses = responses[start:end]
            
            embed = discord.Embed(
                title='📝 الردود التلقائية',
                description=f'إجمالي الردود: **{len(responses)}**',
                color=discord.Color.blue()
            )
            
            for i, resp in enumerate(page_responses, start=start + 1):
                status = '✅ مفعل' if resp.get('enabled', 1) else '❌ معطل'
                trigger_type = resp.get('trigger_type', 'contains')
                chance = resp.get('chance', 100)
                cooldown = resp.get('cooldown', 0)
                
                # اختصار الرد إذا كان طويلاً
                response_text = resp['response']
                if len(response_text) > 100:
                    response_text = response_text[:97] + '...'
                
                value_parts = [
                    f'**المحفز:** `{resp["trigger"]}`',
                    f'**النوع:** {trigger_type}',
                    f'**الرد:** {response_text}',
                ]
                
                if chance < 100:
                    value_parts.append(f'**الاحتمالية:** {chance}%')
                
                if cooldown > 0:
                    value_parts.append(f'**الانتظار:** {cooldown}s')
                
                embed.add_field(
                    name=f'{status} #{i} • ID: `{resp["id"]}`',
                    value='\n'.join(value_parts),
                    inline=False
                )
            
            embed.set_footer(text=f'الصفحة {page}/{total_pages}')
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            bot_logger.exception('خطأ في list_responses', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== تفاصيل رد ====================
    
    @ar_group.command(name='info', description='عرض تفاصيل رد معين')
    @app_commands.describe(id='معرف الرد')
    async def response_info(interaction: discord.Interaction, id: int):
        """تفاصيل رد محدد"""
        try:
            responses = await autoresponse_system.get_responses(str(interaction.guild.id))
            response = next((r for r in responses if r['id'] == id), None)
            
            if not response:
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', f'لم يتم العثور على رد بـ ID: {id}'),
                    ephemeral=True
                )
                return
            
            status = '✅ مفعل' if response.get('enabled', 1) else '❌ معطل'
            
            embed = discord.Embed(
                title=f'📝 تفاصيل الرد #{id}',
                color=discord.Color.blue()
            )
            
            embed.add_field(name='الحالة', value=status, inline=True)
            embed.add_field(name='ID', value=f'`{id}`', inline=True)
            embed.add_field(name='النوع', value=response.get('trigger_type', 'contains'), inline=True)
            
            embed.add_field(name='المحفز', value=f'```{response["trigger"]}```', inline=False)
            embed.add_field(name='الرد', value=response['response'], inline=False)
            
            embed.add_field(name='الاحتمالية', value=f'{response.get("chance", 100)}%', inline=True)
            embed.add_field(name='الانتظار', value=f'{response.get("cooldown", 0)}s', inline=True)
            
            if response.get('last_used'):
                embed.add_field(
                    name='آخر استخدام',
                    value=f'<t:{int(response["last_used"])}:R>',
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            bot_logger.exception('خطأ في response_info', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== حذف رد ====================
    
    @ar_group.command(name='remove', description='حذف رد تلقائي')
    @app_commands.describe(id='معرف الرد')
    @permissions.is_admin()
    async def remove_response(interaction: discord.Interaction, id: int):
        """حذف رد"""
        try:
            success = await autoresponse_system.remove_response(id)
            
            if success:
                await interaction.response.send_message(
                    embed=embeds.success_embed(
                        'تم الحذف',
                        f'تم حذف الرد التلقائي #{id} بنجاح'
                    )
                )
                bot_logger.info(f'تم حذف رد تلقائي #{id} في {interaction.guild.name}')
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        f'لم يتم العثور على رد بـ ID: {id}'
                    ),
                    ephemeral=True
                )
                
        except Exception as e:
            bot_logger.exception('خطأ في remove_response', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== تفعيل/تعطيل ====================
    
    @ar_group.command(name='toggle', description='تفعيل/تعطيل رد تلقائي')
    @app_commands.describe(id='معرف الرد')
    @permissions.is_admin()
    async def toggle_response(interaction: discord.Interaction, id: int):
        """تبديل حالة الرد"""
        try:
            success = await autoresponse_system.toggle_response(id)
            
            if success:
                await interaction.response.send_message(
                    embed=embeds.success_embed(
                        'تم',
                        f'تم تغيير حالة الرد #{id}\n\n'
                        'استخدم `/autoresponse info` للتحقق من الحالة الجديدة'
                    )
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        f'لم يتم العثور على رد بـ ID: {id}'
                    ),
                    ephemeral=True
                )
                
        except Exception as e:
            bot_logger.exception('خطأ في toggle_response', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== تعديل رد ====================
    
    @ar_group.command(name='edit', description='تعديل رد تلقائي')
    @app_commands.describe(
        id='معرف الرد',
        trigger='المحفز الجديد (اختياري)',
        response='الرد الجديد (اختياري)',
        chance='الاحتمالية الجديدة (اختياري)',
        cooldown='الانتظار الجديد (اختياري)'
    )
    @permissions.is_admin()
    async def edit_response(
        interaction: discord.Interaction,
        id: int,
        trigger: Optional[str] = None,
        response: Optional[str] = None,
        chance: Optional[int] = None,
        cooldown: Optional[int] = None
    ):
        """تعديل رد موجود"""
        try:
            if not any([trigger, response, chance, cooldown]):
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'تحذير',
                        'يجب تحديد شيء واحد على الأقل للتعديل'
                    ),
                    ephemeral=True
                )
                return
            
            # التحقق من الاحتمالية
            if chance is not None and (chance < 0 or chance > 100):
                await interaction.response.send_message(
                    embed=embeds.error_embed('خطأ', 'الاحتمالية يجب أن تكون بين 0-100'),
                    ephemeral=True
                )
                return
            
            await autoresponse_system.update_response(
                id,
                trigger=trigger,
                response=response,
                chance=chance,
                cooldown=cooldown
            )
            
            embed = discord.Embed(
                title='✅ تم التعديل',
                description=f'تم تحديث الرد #{id}',
                color=discord.Color.green()
            )
            
            if trigger:
                embed.add_field(name='المحفز الجديد', value=f'`{trigger}`', inline=False)
            if response:
                embed.add_field(name='الرد الجديد', value=response, inline=False)
            if chance is not None:
                embed.add_field(name='الاحتمالية الجديدة', value=f'{chance}%', inline=True)
            if cooldown is not None:
                embed.add_field(name='الانتظار الجديد', value=f'{cooldown}s', inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            bot_logger.info(f'تم تعديل رد #{id} في {interaction.guild.name}')
            
        except Exception as e:
            bot_logger.exception('خطأ في edit_response', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== القوالب الجاهزة ====================
    
    @ar_group.command(name='templates', description='عرض القوالب الجاهزة')
    async def show_templates(interaction: discord.Interaction):
        """عرض القوالب"""
        templates = autoresponse_system.get_template_responses()
        
        embed = discord.Embed(
            title='📋 القوالب الجاهزة',
            description='قوالب جاهزة للاستخدام الفوري',
            color=discord.Color.green()
        )
        
        for i, template in enumerate(templates, 1):
            embed.add_field(
                name=f'{i}. {template["trigger"]}',
                value=(
                    f'**الرد:** {template["response"]}\n'
                    f'**النوع:** {template["trigger_type"]}\n'
                    f'`/autoresponse addtemplate id:{i}`'
                ),
                inline=False
            )
        
        embed.set_footer(text='استخدم /autoresponse addtemplate لإضافة قالب')
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ar_group.command(name='addtemplate', description='إضافة قالب جاهز')
    @app_commands.describe(id='رقم القالب (1-8)')
    @permissions.is_admin()
    async def add_template(interaction: discord.Interaction, id: int):
        """إضافة قالب"""
        try:
            response_id = await autoresponse_system.add_template(
                str(interaction.guild.id),
                id - 1  # التحويل لـ 0-indexed
            )
            
            if response_id:
                templates = autoresponse_system.get_template_responses()
                template = templates[id - 1] if 0 < id <= len(templates) else None
                
                if template:
                    embed = embeds.success_embed(
                        'تم إضافة القالب',
                        f'**المحفز:** {template["trigger"]}\n'
                        f'**الرد:** {template["response"]}\n'
                        f'**ID الجديد:** `{response_id}`'
                    )
                else:
                    embed = embeds.success_embed('تم', f'تم إضافة القالب #{id}')
                
                await interaction.response.send_message(embed=embed)
                
                bot_logger.info(f'تم إضافة قالب #{id} في {interaction.guild.name}')
            else:
                await interaction.response.send_message(
                    embed=embeds.error_embed(
                        'خطأ',
                        f'رقم قالب غير صحيح. استخدم رقم بين 1-8'
                    ),
                    ephemeral=True
                )
                
        except Exception as e:
            bot_logger.exception('خطأ في add_template', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== الإحصائيات ====================
    
    @ar_group.command(name='stats', description='إحصائيات الردود التلقائية')
    async def stats(interaction: discord.Interaction):
        """إحصائيات"""
        try:
            stats = await autoresponse_system.get_response_stats(str(interaction.guild.id))
            
            if stats['total'] == 0:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لا توجد ردود',
                        'لم يتم إضافة أي ردود تلقائية بعد'
                    ),
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title='📊 إحصائيات الردود التلقائية',
                color=discord.Color.blue()
            )
            
            embed.add_field(name='الإجمالي', value=f'`{stats["total"]}`', inline=True)
            embed.add_field(name='المفعلة', value=f'`{stats["enabled"]}`', inline=True)
            embed.add_field(name='المعطلة', value=f'`{stats["disabled"]}`', inline=True)
            
            if stats['by_type']:
                types_text = '\n'.join([
                    f'• **{type}:** {count}'
                    for type, count in stats['by_type'].items()
                ])
                embed.add_field(name='حسب النوع', value=types_text, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            bot_logger.exception('خطأ في stats', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== البحث ====================
    
    @ar_group.command(name='search', description='البحث في الردود التلقائية')
    @app_commands.describe(query='كلمة البحث')
    async def search(interaction: discord.Interaction, query: str):
        """بحث"""
        try:
            results = await autoresponse_system.search_responses(
                str(interaction.guild.id),
                query=query
            )
            
            if not results:
                await interaction.response.send_message(
                    embed=embeds.warning_embed(
                        'لا توجد نتائج',
                        f'لم يتم العثور على ردود تحتوي على: `{query}`'
                    ),
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f'🔍 نتائج البحث: "{query}"',
                description=f'تم العثور على {len(results)} رد',
                color=discord.Color.blue()
            )
            
            for resp in results[:5]:  # أول 5 نتائج
                status = '✅' if resp.get('enabled', 1) else '❌'
                embed.add_field(
                    name=f'{status} #{resp["id"]} - {resp["trigger"]}',
                    value=f'**الرد:** {resp["response"][:100]}...',
                    inline=False
                )
            
            if len(results) > 5:
                embed.set_footer(text=f'عرض 5 من أصل {len(results)} نتيجة')
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            bot_logger.exception('خطأ في search', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    # ==================== مسح الكل ====================
    
    @ar_group.command(name='clear', description='⚠️ حذف جميع الردود التلقائية')
    @permissions.is_admin()
    async def clear_all(interaction: discord.Interaction):
        """حذف جميع الردود"""
        try:
            responses = await autoresponse_system.get_responses(str(interaction.guild.id))
            
            if not responses:
                await interaction.response.send_message(
                    embed=embeds.warning_embed('لا توجد ردود', 'لا توجد ردود لحذفها'),
                    ephemeral=True
                )
                return
            
            # تأكيد
            embed = discord.Embed(
                title='⚠️ تحذير',
                description=(
                    f'أنت على وشك حذف **{len(responses)}** رد تلقائي!\n\n'
                    '**هذا الإجراء لا يمكن التراجع عنه!**\n\n'
                    'اضغط على الزر أدناه للتأكيد'
                ),
                color=discord.Color.red()
            )
            
            view = ConfirmClearView(interaction.guild.id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            bot_logger.exception('خطأ في clear_all', e)
            await interaction.response.send_message(
                embed=embeds.error_embed('خطأ', str(e)),
                ephemeral=True
            )
    
    bot.tree.add_command(ar_group)
    bot_logger.success('✅ تم تسجيل أوامر الردود التلقائية')


# ==================== Confirm View ====================

class ConfirmClearView(discord.ui.View):
    """عرض تأكيد الحذف"""
    
    def __init__(self, guild_id: str):
        super().__init__(timeout=30)
        self.guild_id = guild_id
        self.confirmed = False
    
    @discord.ui.button(label='تأكيد الحذف', style=discord.ButtonStyle.danger, emoji='🗑️')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """تأكيد"""
        try:
            responses = await autoresponse_system.get_responses(self.guild_id)
            count = len(responses)
            
            # حذف جميع الردود
            for resp in responses:
                await autoresponse_system.remove_response(resp['id'])
            
            embed = embeds.success_embed(
                'تم الحذف',
                f'تم حذف {count} رد تلقائي بنجاح'
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            bot_logger.warning(f'تم حذف جميع الردود التلقائية ({count}) في {interaction.guild.name}')
            
        except Exception as e:
            bot_logger.exception('خطأ في confirm clear', e)
            await interaction.response.edit_message(
                embed=embeds.error_embed('خطأ', str(e)),
                view=None
            )
    
    @discord.ui.button(label='إلغاء', style=discord.ButtonStyle.secondary, emoji='❌')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """إلغاء"""
        await interaction.response.edit_message(
            embed=embeds.warning_embed('تم الإلغاء', 'لم يتم حذف أي شيء'),
            view=None
        )
📚 دليل الأوامر الجديدة - v2.0

🤖 الردود التلقائية

/autoresponse add

إضافة رد تلقائي بسيط

/autoresponse add trigger:"سلام عليكم" response:"وعليكم السلام" type:contains 

المتغيرات المتاحة:

{mention} - منشن العضو

{user} - اسم العضو

{server} - اسم السيرفر

{membercount} - عدد الأعضاء

{channel} - اسم القناة

/autoresponse addadvanced

رد متقدم مع إعدادات إضافية

/autoresponse addadvanced trigger:"هلا" response:"هلا والله {mention}!" type:contains chance:80 cooldown:60 

الخيارات:

chance - احتمالية الرد (0-100)

cooldown - وقت الانتظار بالثواني

/autoresponse list

عرض جميع الردود

/autoresponse list page:1 

/autoresponse info

تفاصيل رد معين

/autoresponse info id:5 

/autoresponse remove

حذف رد

/autoresponse remove id:5 

/autoresponse toggle

تفعيل/تعطيل رد

/autoresponse toggle id:5 

/autoresponse edit

تعديل رد موجود

/autoresponse edit id:5 response:"رد جديد" chance:100 

/autoresponse templates

عرض القوالب الجاهزة

/autoresponse addtemplate

إضافة قالب جاهز

/autoresponse addtemplate id:1 

/autoresponse stats

إحصائيات الردود

/autoresponse search

البحث في الردود

/autoresponse search query:"سلام" 

/autoresponse clear

⚠️ حذف جميع الردود (يطلب تأكيد)

🗳️ الاستطلاعات

/poll create

إنشاء استطلاع كامل

/poll create question:"ما هي أفضل لعبة؟" options:"فورتنايت|كول اوف ديوتي|فالورانت|ماين كرافت" duration:60 multiple:false anonymous:false 

ملاحظات:

افصل الخيارات بـ |

الحد الأقصى 10 خيارات

المدة بالدقائق (1-10080)

/poll quick

استطلاع سريع (نعم/لا)

/poll quick question:"هل توافق؟" duration:5 

/poll close

إغلاق استطلاع مبكراً

/poll close poll_id:1 

فقط منشئ الاستطلاع أو المشرفين

/poll results

عرض النتائج الحالية

/poll results poll_id:1 

/poll myvote

عرض صوتك في استطلاع

/poll myvote poll_id:1 

📨 الدعوات

/invites check

عرض عدد دعوات عضو

/invites check @user /invites check # دعواتك 

/invites leaderboard

لوحة صدارة الدعوات

/invites leaderboard limit:10 

/invites whoinvited

معرفة من دعا عضواً

/invites whoinvited @user 

/invites inviterewards add

إضافة مكافأة دعوات

/invites inviterewards add invites:5 role:@VIP 

أمثلة للمكافآت:

/invites inviterewards add invites:5 role:@Bronze /invites inviterewards add invites:10 role:@Silver /invites inviterewards add invites:25 role:@Gold /invites inviterewards add invites:50 role:@Diamond 

/invites inviterewards remove

حذف مكافأة

/invites inviterewards remove invites:5 

/invites inviterewards list

عرض جميع المكافآت

📊 الإحصائيات

/analytics

إحصائيات شاملة للسيرفر

/analytics days:7 # آخر أسبوع /analytics days:30 # آخر شهر 

تشمل:

عدد الأعضاء والبوتات والمتصلين

عدد القنوات

الرسائل والنشاط

الانضمامات والمغادرات

إحصائيات المستويات

رسم بياني نصي

/topusers

أكثر الأعضاء نشاطاً

/topusers limit:10 /topusers limit:25 # حد أقصى 

🎯 سيناريوهات الاستخدام

سيناريو 1: إعداد ردود تلقائية كاملة

# ردود السلام /autoresponse add trigger:"السلام عليكم" response:"وعليكم السلام ورحمة الله 🌹" /autoresponse add trigger:"صباح الخير" response:"صباح النور ☀️" /autoresponse add trigger:"مساء الخير" response:"مساء النور 🌙" # ردود مع cooldown /autoresponse addadvanced trigger:"شكراً" response:"العفو {mention}! ❤️" cooldown:120 # ردود بـ chance /autoresponse addadvanced trigger:"هلا" response:"هلا والله!" chance:70 cooldown:60 # استخدام القوالب /autoresponse templates /autoresponse addtemplate id:1 /autoresponse addtemplate id:2 

سيناريو 2: استطلاع أسبوعي

# استطلاع اللعبة المفضلة /poll create question:"🎮 ما هي اللعبة التي ستلعبها هذا الأسبوع؟" options:"فورتنايت|كول اوف ديوتي|فالورانت|ماين كرافت|أبيكس ليجندز" duration:10080 multiple:false anonymous:false # استطلاع فعالية /poll create question:"🎉 أي فعالية تفضل؟ (يمكن اختيار أكثر من واحد)" options:"بطولة|حفلة|مسابقة|عرض" duration:4320 multiple:true anonymous:false 

سيناريو 3: نظام دعوات مع مكافآت

# إعداد المكافآت /invites inviterewards add invites:3 role:@Friend /invites inviterewards add invites:5 role:@Active /invites inviterewards add invites:10 role:@Loyal /invites inviterewards add invites:25 role:@Champion /invites inviterewards add invites:50 role:@Legend # عرض المكافآت للأعضاء /invites inviterewards list # التحقق من الدعوات /invites check /invites leaderboard limit:10 

سيناريو 4: مراقبة النشاط

# إحصائيات يومية /analytics days:1 # إحصائيات أسبوعية /analytics days:7 # أكثر الأعضاء نشاطاً /topusers limit:10 # دعوات السيرفر /invites leaderboard limit:15 

💡 نصائح وحيل

نصيحة 1: الردود التلقائية الذكية

# رد بناءً على الوقت morning: صباح الخير → صباح النور ☀️ evening: مساء الخير → مساء النور 🌙 # ردود مشجعة شكراً → العفو {mention}! نحن هنا لخدمتك ❤️ 

نصيحة 2: استطلاعات فعالة

استخدم quick للقرارات السريعة

استخدم multiple:true للاستبيانات

استخدم anonymous:true للمواضيع الحساسة

اختصر الخيارات لـ 5-6 خيارات للنتائج الأفضل

نصيحة 3: تحفيز الدعوات

# مكافآت تدريجية 3 دعوات → Friend 5 دعوات → Active 10 دعوات → Loyal + لون خاص 25 دعوات → Champion + صلاحيات 50 دعوات → Legend + دور VIP 

نصيحة 4: تتبع النشاط

افحص الإحصائيات كل يوم أحد

قارن بين الأسابيع

كافئ الأعضاء النشطين

تحقق من /topusers شهرياً

⚙️ الأعدادات الموصى بها

للسيرفرات الصغيرة (< 100)

# 3-5 ردود تلقائية بسيطة /autoresponse addtemplate id:1 /autoresponse addtemplate id:2 /autoresponse addtemplate id:3 # استطلاعات أسبوعية duration: 10080 (أسبوع) # مكافآت بسيطة 3 → Friend 10 → VIP 

للسيرفرات المتوسطة (100-1000)

# 5-10 ردود بـ cooldowns cooldown: 60-120 ثانية # استطلاعات متعددة يومي: quick polls أسبوعي: استطلاع كامل # مكافآت متدرجة 5, 10, 25, 50 دعوات 

للسيرفرات الكبيرة (1000+)

# 10+ ردود متقدمة cooldown: 120-300 ثانية chance: 70-90% # استطلاعات منظمة يومي + أسبوعي + شهري # مكافآت ضخمة 10, 25, 50, 100, 250 دعوات 

🔗 روابط مفيدة

README الأصلي: README.md

دليل البدء السريع: QUICKSTART.md

التحديثات: UPDATE_V2.0.md

السجلات: bot.log

آخر تحديث: ديسمبر 2024


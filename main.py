import telebot
from telebot import types

# 1. الإعدادات
TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
CHANNEL_ID = "@haithamMax1"
bot = telebot.TeleBot(TOKEN)

# 2. قاعدة البيانات (يمكنك تغيير الروابط هنا)
DATA = {
    "tools": {
        "tsm_pro": ("⚙️ TSM Tool Pro", "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"),
        "dft_pro": ("⚡ DFT Pro Tool", "https://www.mediafire.com/file/afpqr6duvxavdjf/DFTPRO_v7.0.7.exe/file"),
        "chimera": ("🧬 Chimera Tool", "https://chimeratool.com/downloads/latest"),
        "sigma_main": ("🔋 Sigma Plus (البرنامج)", "https://sigmakey.com/nfs/content/5802/file/sigmaplus-software-setup-v1.01.11.ehe"),
        "sigma_kirin": ("🔋 Sigma Kirin Files", "https://mega.nz/file/HpgniKDT#OjCTB2_Ki_TxcKs7mCBNgd08eDVa1jPwOsU1aci0KXU"),
        "sigma_exynos": ("🔋 Sigma Exynos Files", "https://www.mediafire.com/file/fwqvfmq5om67t69/exynos.rar/file"),
        "unlock_tool": ("🔓 UnlockTool", "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file")
    },
    "drivers": {
        "adb": ("Adb Driver", "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"),
        "samsung": ("Samsung All USB", "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file"),
        "mtk": ("MTK Driver", "ضع_رابط_MTK_هنا"),
        "qualcomm": ("Qualcomm Driver", "ضع_رابط_Qualcomm_هنا")
    },
    "fixes": {
        "frp": ("🔥 تخطي FRP Samsung", "اكتب الكود: *#0*# ثم استخدم أداة TSM"),
        "bootloop": ("⚡ حل مشكلة تعليق الشعار", "جرب تفليش ملف System فقط")
    }
}

# دالة التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("💡 حلول ومشاكل", callback_data="main_fixes"),
        types.InlineKeyboardButton("💬 تواصل معي", callback_data="contact_us")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في نظام HMAX الذكي.\nاختر قسماً من القائمة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "main_tools":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k, v in DATA["tools"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"link_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚙️ اختر الأداة:", reply_markup=markup)
    
    elif call.data == "main_drivers":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k, v in DATA["drivers"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"link_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💾 اختر التعريف:", reply_markup=markup)

    elif call.data.startswith("link_"):
        # تم تغيير الشرط ليعمل معك فوراً بدون اشتراك إجباري للتجربة، أعده لـ if is_subscribed إذا أردت الحماية
        if True: 
            key = call.data.split("_")[-1]
            data_dict = DATA["tools"] if key in DATA["tools"] else DATA["drivers"]
            link = data_dict[key][1]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ الرابط المباشر:\n{link}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
    
    elif call.data == "main_fixes":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k, v in DATA["fixes"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"fix_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💡 حلول سريعة:", reply_markup=markup)
    
    elif call.data.startswith("fix_"):
        key = call.data.replace("fix_", "")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"💡 {DATA['fixes'][key][0]}:\n{DATA['fixes'][key][1]}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_fixes")))

    elif call.data == "contact_us":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax"))
        bot.send_message(call.message.chat.id, "💬 تواصل معي:", reply_markup=markup)
        
    elif call.data == "back_start":
        start(call.message)

print("Haitham Max System is running...")
bot.infinity_polling()

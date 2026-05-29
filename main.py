import telebot
from telebot import types

# 1. الإعدادات
TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
MY_CHAT_ID = "560330933"
CHANNEL_ID = "@haithamMax1"
bot = telebot.TeleBot(TOKEN)

# 2. قاعدة البيانات
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
        "samsung": ("Samsung All USB", "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file")
    },
    "fixes": {
        "frp": ("🔥 تخطي FRP Samsung", "اكتب الكود: *#0*# ثم استخدم أداة TSM"),
        "bootloop": ("⚡ حل مشكلة تعليق الشعار", "جرب تفليش ملف System فقط")
    },
    "server_status": "🏢 **قائمة Max Tech Server**\nترسانة الأدوات المتاحة حالياً:\n✅ EFT Dongle: 6 | ✅ Hydra: 3 | ✅ Octoplus: 4\n✅ UMT Pro+NCK: 5 | ✅ SigmaPlus: 1 | ✅ Z3X: 2\nتحديث: 29 مايو 2026"
}

def save_user(user_id):
    try:
        with open("users.txt", "a") as f: f.write(str(user_id) + "\n")
    except: pass

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("🖥 Max Tech Server", callback_data="server_status"),
        types.InlineKeyboardButton("💡 حلول ومشاكل", callback_data="main_fixes"),
        types.InlineKeyboardButton("📝 طلب أداة خاصة", callback_data="request_tool"),
        types.InlineKeyboardButton("💬 تواصل معي", callback_data="contact_us")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في نظام HMAX الذكي.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "main_tools": callback_main_tools(call.message)
    elif call.data == "main_drivers": callback_main_drivers(call.message)
    elif call.data == "server_status":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=DATA["server_status"], parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
    elif call.data == "main_fixes":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k, v in DATA["fixes"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"fix_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💡 حلول سريعة:", reply_markup=markup)
    elif call.data == "contact_us": contact_us(call.message)
    elif call.data == "back_start": start(call.message)
    elif call.data.startswith("link_"):
        if is_subscribed(call.message.chat.id):
            key = call.data.split("_")[-1]
            link = DATA["tools"].get(key, DATA["drivers"].get(key))[1]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ الرابط:\n{link}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚠️ اشترك في القناة للوصول.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📢 اشترك الآن", url="https://t.me/haithamMax1"), types.InlineKeyboardButton("🔄 تحقق", callback_data=call.data)))
    elif call.data.startswith("fix_"):
        key = call.data.replace("fix_", "")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"💡 {DATA['fixes'][key][0]}:\n{DATA['fixes'][key][1]}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_fixes")))

def callback_main_tools(msg):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for k, v in DATA["tools"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"link_{k}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="⚙️ اختر الأداة:", reply_markup=markup)

def callback_main_drivers(msg):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for k, v in DATA["drivers"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"link_{k}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="💾 اختر التعريف:", reply_markup=markup)

def contact_us(msg):
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax"), types.InlineKeyboardButton("📱 واتساب", url="https://wa.me/967772773388"))
    bot.send_message(msg.chat.id, "💬 تواصل معي عبر:", reply_markup=markup)

bot.infinity_polling()

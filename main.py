import telebot
from telebot import types

TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
MY_CHAT_ID = "560330933"
CHANNEL_ID = "@haithamMax1" # معرف قناتك
bot = telebot.TeleBot(TOKEN)

DATA = {
    "tools": {
        "tsm_pro": ("⚙️ TSM Tool Pro", "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"),
        "tsm_edition": ("🔧 TSM Pro Edition", "https://www.mediafire.com/file/j4d1v5wwoodbm4r/TSM+Pro+Edition+Setup%5B2026-05-28%5D.7z/file"),
        "unlock_tool": ("🔓 UnlockTool", "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file")
    },
    "drivers": {
        "adb": ("Adb Driver", "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"),
        "qcom_mtk": ("Univ. QCOM-MTK-ADB", "https://www.mediafire.com/file_premium/ko4na2ox2rcytbc/generic_usb_driver%257BQLM-MTK-ADB%257Dv1.1.0.zip/file"),
        "qcom": ("QCOM Driver", "https://www.mediafire.com/file_premium/ko4na2ox2rcytbc/generic_usb_driver%257BQLM-MTK-ADB%257Dv1.1.0.zip/file"),
        "sprd": ("Sprd Driver", "https://www.mediafire.com/file_premium/a6y49zbrdky5lmk/Spreadtrum_77xx_Drivers.7z/file"),
        "mtk": ("MTK Driver", "https://www.mediafire.com/file_premium/0psu8awm57or6jj/drivers_mtk_v2.0.1.1_2.7z/file"),
        "samsung": ("Samsung All USB", "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file"),
        "fastboot": ("FASTBOOT DRIVER", "https://mega.nz/file/w0plHSKZ#TjvkWuc9OmOpQiJq7Nr0U-ANlPVyf7RP1-2KvcgaSO4"),
        "exynos": ("Exynos driver", "https://mega.nz/file/ksYGmJ6T#_7DeakMDKI9lPkGIvUA0TIN9qHGCUtSrDfTDAump3WU"),
        "com1": ("COM1-fastboot", "https://mega.nz/file/M9IgjQxB#lPAouwiWNAwxPjfKuj0OQT1fqcplCKjyeCdIb7WFSqQ"),
        "adb_fix": ("حل مشكلة ADB", "https://mega.nz/file/UgZwSCRS#rgIJ8Wdli6yG_m6V7aWzJZmrVLIfHTrzQWZUhvU6Ums")
    }
}

# دالة التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("📝 طلب أداة خاصة", callback_data="request_tool"),
        types.InlineKeyboardButton("📢 قناة الأخبار", url="https://t.me/haithamMax1"),
        types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax"),
        types.InlineKeyboardButton("📱 واتساب", url="https://wa.me/967772773388")
    )
    bot.send_message(message.chat.id, "👑 مرحباً بك في HMAX Global System\nنظام صيانة متكامل بين يديك.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "request_tool":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="📝 أرسل اسم الأداة التي تحتاجها:")
        bot.register_next_step_handler(call.message, process_request)
    
    elif call.data == "main_tools":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, value in DATA["tools"].items():
            markup.add(types.InlineKeyboardButton(value[0], callback_data=f"link_{key}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="⚙️ اختر الأداة:", reply_markup=markup)
        
    elif call.data == "main_drivers":
        markup = types.InlineKeyboardMarkup(row_width=2)
        for key, value in DATA["drivers"].items():
            markup.add(types.InlineKeyboardButton(value[0], callback_data=f"link_{key}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="💾 اختر التعريف:", reply_markup=markup)
        
    elif call.data == "back_start":
        start(call.message)
        bot.delete_message(chat_id, call.message.message_id)
        
    elif call.data.startswith("link_"):
        key = call.data.replace("link_", "")
        if is_subscribed(chat_id):
            link = DATA["tools"][key][1] if key in DATA["tools"] else DATA["drivers"][key][1]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_start"))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"✅ الرابط المباشر:\n{link}", reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📢 اشترك في القناة أولاً", url="https://t.me/haithamMax1"))
            markup.add(types.InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data=call.data))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="⚠️ يجب الاشتراك في القناة للوصول للرابط.", reply_markup=markup)

def process_request(message):
    bot.send_message(MY_CHAT_ID, f"🔔 طلب جديد من {message.from_user.first_name}:\n{message.text}")
    bot.send_message(message.chat.id, "✅ تم إرسال طلبك، شكراً لك!")
    start(message)

print("HMAX System is running...")
bot.infinity_polling()

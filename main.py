import telebot
from telebot import types
from flask import Flask
from threading import Thread

TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
MY_CHAT_ID = "560330933"
bot = telebot.TeleBot(TOKEN)

# تشغيل سيرفر الويب ليبقى البوت حياً
app = Flask(__name__)
@app.route('/')
def home(): return "HMAX System is running!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

DATA = {
    "tools": {
        "tsm_pro": ("⚙️ TSM Tool Pro", "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"),
        "tsm_edition": ("🔧 TSM Pro Edition", "https://www.mediafire.com/file/j4d1v5wwoodbm4r/TSM+Pro+Edition+Setup%5B2026-05-28%5D.7z/file"),
        "unlock_tool": ("🔓 UnlockTool", "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file"),
        "dft_pro": ("⚡ DFT Pro Tool", "https://www.mediafire.com/file/afpqr6duvxavdjf/DFTPRO_v7.0.7.exe/file"),
        "sigma": ("🔋 Sigma Plus", "https://sigmakey.com/nfs/content/5802/file/sigmaplus-software-setup-v1.01.11.ehe")
    },
    "drivers": {
        "adb": ("Adb Driver", "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"),
        "qcom_mtk": ("Univ. QCOM-MTK-ADB", "https://www.mediafire.com/file_premium/ko4na2ox2rcytbc/generic_usb_driver%257BQLM-MTK-ADB%257Dv1.1.0.zip/file"),
        "mtk": ("MTK Driver", "https://www.mediafire.com/file_premium/0psu8awm57or6jj/drivers_mtk_v2.0.1.1_2.7z/file"),
        "samsung": ("Samsung All USB", "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file"),
        "fastboot": ("FASTBOOT DRIVER", "https://mega.nz/file/w0plHSKZ#TjvkWuc9OmOpQiJq7Nr0U-ANlPVyf7RP1-2KvcgaSO4"),
        "exynos": ("Exynos driver", "https://mega.nz/file/ksYGmJ6T#_7DeakMDKI9lPkGIvUA0TIN9qHGCUtSrDfTDAump3WU"),
        "adb_fix": ("حل مشكلة ADB", "https://mega.nz/file/UgZwSCRS#rgIJ8Wdli6yG_m6V7aWzJZmrVLIfHTrzQWZUhvU6Ums")
    }
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("📝 طلب أداة خاصة", callback_data="req_tool"),
        types.InlineKeyboardButton("📢 قناة الأخبار", url="https://t.me/haithamMax1"),
        types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax")
    )
    bot.send_message(message.chat.id, "👑 مرحباً بك في HMAX Global System\nنظام صيانة متكامل بين يديك.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "back_start": start(call.message)
    elif call.data == "main_tools":
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
        key = call.data.replace("link_", "")
        link = DATA["tools"].get(key, DATA["drivers"].get(key))[1]
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_tools" if key in DATA["tools"] else "main_drivers"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ الرابط:\n{link}", reply_markup=markup)
    elif call.data == "req_tool":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="📝 أرسل اسم الأداة:")
        bot.register_next_step_handler(call.message, lambda msg: [bot.send_message(MY_CHAT_ID, f"طلب جديد: {msg.text}"), bot.send_message(msg.chat.id, "✅ تم إرسال الطلب!"), start(msg)])

print("System is running...")
bot.infinity_polling()

import telebot
from telebot import types
from flask import Flask
from threading import Thread

TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
MY_CHAT_ID = "560330933"
bot = telebot.TeleBot(TOKEN)

# تشغيل سيرفر الويب
app = Flask(__name__)
@app.route('/')
def home(): return "HMAX System is running!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

DATA = {
    "tools": {
        "tsm_pro": ("⚙️ TSM Tool Pro", "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"),
        "dft_pro": ("⚡ DFT Pro Tool", "https://www.mediafire.com/file/afpqr6duvxavdjf/DFTPRO_v7.0.7.exe/file"),
        "unlock_tool": ("🔓 UnlockTool", "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file"),
        "sigma_main": ("🔋 Sigma Plus (البرنامج)", "https://sigmakey.com/nfs/content/5802/file/sigmaplus-software-setup-v1.01.11.ehe"),
        "sigma_kirin": ("🔋 ملفات Kirin", "https://mega.nz/file/HpgniKDT#OjCTB2_Ki_TxcKs7mCBNgd08eDVa1jPwOsU1aci0KXU"),
        "sigma_exynos": ("🔋 ملفات Exynos", "https://www.mediafire.com/file/fwqvfmq5om67t69/exynos.rar/file")
    },
    "drivers": {
        "adb": ("Adb Driver", "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"),
        "mtk": ("MTK Driver", "https://www.mediafire.com/file_premium/0psu8awm57or6jj/drivers_mtk_v2.0.1.1_2.7z/file"),
        "samsung": ("Samsung All USB", "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file")
    }
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("📝 طلب أداة", callback_data="req_tool"),
        types.InlineKeyboardButton("📱 واتساب", url="https://wa.me/967772773388"),
        types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في HMAX Global System.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "back_start": start(call.message)
    
    elif call.data == "main_tools":
        markup = types.InlineKeyboardMarkup(row_width=1)
        # تخصيص قائمة السيجما
        markup.add(types.InlineKeyboardButton("⚙️ TSM Tool Pro", callback_data="link_tsm_pro"))
        markup.add(types.InlineKeyboardButton("⚡ DFT Pro Tool", callback_data="link_dft_pro"))
        markup.add(types.InlineKeyboardButton("🔋 Sigma Plus (الخيارات)", callback_data="sigma_options"))
        markup.add(types.InlineKeyboardButton("🔓 UnlockTool", callback_data="link_unlock_tool"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚙️ اختر الأداة:", reply_markup=markup)
        
    elif call.data == "sigma_options":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("1️⃣ تحميل البرنامج", callback_data="link_sigma_main"),
            types.InlineKeyboardButton("2️⃣ ملفات Kirin", callback_data="link_sigma_kirin"),
            types.InlineKeyboardButton("3️⃣ ملفات Exynos", callback_data="link_sigma_exynos"),
            types.InlineKeyboardButton("🔙 رجوع للأدوات", callback_data="main_tools")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔋 اختر المطلوب لـ Sigma:", reply_markup=markup)

    elif call.data == "main_drivers":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k, v in DATA["drivers"].items(): markup.add(types.InlineKeyboardButton(v[0], callback_data=f"link_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💾 اختر التعريف:", reply_markup=markup)
        
    elif call.data.startswith("link_"):
        key = call.data.replace("link_", "")
        link = DATA["tools"].get(key, DATA["drivers"].get(key))[1]
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_tools" if "sigma" in key or "tsm" in key or "dft" in key or "unlock" in key else "main_drivers"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"✅ الرابط المباشر:\n{link}", reply_markup=markup)
        
    elif call.data == "req_tool":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="📝 أرسل اسم الأداة:")
        bot.register_next_step_handler(call.message, lambda msg: [bot.send_message(MY_CHAT_ID, f"طلب: {msg.text}"), bot.send_message(msg.chat.id, "✅ تم إرسال طلبك!"), start(msg)])

print("System is running...")
bot.infinity_polling()

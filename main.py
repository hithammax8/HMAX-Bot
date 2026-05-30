import telebot
from telebot import types
from flask import Flask
from threading import Thread
import sqlite3

TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
MY_CHAT_ID = "560330933"
CHANNEL_ID = "@haithamMax1"
bot = telebot.TeleBot(TOKEN)

# الحل الجذري للتعارض
bot.remove_webhook()

# قاعدة بيانات متكاملة
conn = sqlite3.connect('hmax_bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER, inviter INTEGER)')
cursor.execute('CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER)')
conn.commit()

# تشغيل الويب
app = Flask(__name__)
@app.route('/')
def home(): return "HMAX System Active"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

DATA = {
    "tools": {
        "tsm_pro": ("⚙️ TSM Tool Pro", "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"),
        "dft_pro": ("⚡ DFT Pro Tool", "https://www.mediafire.com/file/afpqr6duvxavdjf/DFTPRO_v7.0.7.exe/file"),
        "sigma_main": ("🔋 Sigma Plus (البرنامج)", "https://sigmakey.com/nfs/content/5802/file/sigmaplus-software-setup-v1.01.11.ehe"),
        "sigma_kirin": ("🔋 ملفات Kirin", "https://mega.nz/file/HpgniKDT#OjCTB2_Ki_TxcKs7mCBNgd08eDVa1jPwOsU1aci0KXU"),
        "sigma_exynos": ("🔋 ملفات Exynos", "https://www.mediafire.com/file/fwqvfmq5om67t69/exynos.rar/file"),
        "unlock_tool": ("🔓 UnlockTool", "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file")
    },
    "drivers": {
        "adb": ("Adb Driver", "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"),
        "mtk": ("MTK Driver", "https://www.mediafire.com/file_premium/0psu8awm57or6jj/drivers_mtk_v2.0.1.1_2.7z/file"),
        "samsung": ("Samsung All USB", "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file"),
        "fastboot": ("FASTBOOT DRIVER", "https://mega.nz/file/w0plHSKZ#TjvkWuc9OmOpQiJq7Nr0U-ANlPVyf7RP1-2KvcgaSO4"),
        "exynos": ("Exynos driver", "https://mega.nz/file/ksYGmJ6T#_7DeakMDKI9lPkGIvUA0TIN9qHGCUtSrDfTDAump3WU"),
        "adb_fix": ("حل مشكلة ADB", "https://mega.nz/file/UgZwSCRS#rgIJ8Wdli6yG_m6V7aWzJZmrVLIfHTrzQWZUhvU6Ums")
    }
}

def is_subscribed(user_id):
    try: return bot.get_chat_member(CHANNEL_ID, user_id).status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.is_bot: return
    # تسجيل المستخدم
    cursor.execute("INSERT OR IGNORE INTO users (id, points) VALUES (?, ?)", (message.chat.id, 0))
    conn.commit()
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("📝 طلب أداة", callback_data="req_tool"),
        types.InlineKeyboardButton("💎 نظام النقاط والدعوات", callback_data="points_sys"),
        types.InlineKeyboardButton("📱 واتساب", url="https://wa.me/967772773388"),
        types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في HMAX Global System.", reply_markup=markup)

@bot.message_handler(commands=['dashboard'])
def dashboard(message):
    if str(message.chat.id) == MY_CHAT_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        bot.reply_to(message, f"📊 **لوحة الإدارة**\n👥 المستخدمين: {total}\n🚫 المحظورين: 0\n📝 الطلبات: جاري التحديث...")
    else:
        bot.reply_to(message, "❌ للإدارة فقط.")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.chat.id) == MY_CHAT_ID:
        msg = message.text.replace("/broadcast ", "")
        cursor.execute("SELECT id FROM users")
        for u in cursor.fetchall():
            try: bot.send_message(u[0], msg)
            except: continue
        bot.reply_to(message, "✅ تم الإرسال.")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "back_start": start(call.message)
    elif call.data == "main_tools":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k in DATA["tools"]: markup.add(types.InlineKeyboardButton(DATA["tools"][k][0], callback_data=f"link_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text("⚙️ اختر الأداة:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == "main_drivers":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for k in DATA["drivers"]: markup.add(types.InlineKeyboardButton(DATA["drivers"][k][0], callback_data=f"link_{k}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text("💾 اختر التعريف:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == "points_sys":
        ref_link = f"https://t.me/{(bot.get_me().username)}?start={call.message.chat.id}"
        bot.edit_message_text(f"💎 نظام النقاط\nرابط دعوتك: {ref_link}\nنقاطك: 0", call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
    elif call.data.startswith("link_"):
        key = call.data.replace("link_", "")
        if is_subscribed(call.message.chat.id):
            link = DATA["tools"].get(key, DATA["drivers"].get(key))[1]
            bot.edit_message_text(f"✅ الرابط: {link}", call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
        else:
            bot.answer_callback_query(call.id, "⚠️ اشترك في القناة أولاً!", show_alert=True)
    elif call.data == "req_tool":
        bot.edit_message_text("📝 أرسل اسم الأداة:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, lambda m: [bot.send_message(MY_CHAT_ID, f"🔔 طلب جديد: {m.text}"), start(m)])

print("System is running...")
bot.infinity_polling()

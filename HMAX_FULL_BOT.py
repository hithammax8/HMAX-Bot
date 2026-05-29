
import os
import sqlite3
import logging
import time
from threading import Thread

from flask import Flask
import telebot
from telebot import types

# =========================================
# إعدادات البوت
# =========================================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = str(os.getenv("ADMIN_CHAT_ID", "0"))

CHANNEL_USERNAME = "@yourchannel"

if not TOKEN:
    raise ValueError("يرجى إضافة BOT_TOKEN داخل متغيرات البيئة")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =========================================
# Flask
# =========================================
app = Flask(__name__)

@app.route("/")
def home():
    return "HMAX System Running"

def run_web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# =========================================
# قاعدة البيانات
# =========================================
conn = sqlite3.connect("hmax.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    request TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS banned(
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# =========================================
# حماية سبام
# =========================================
LAST_MESSAGE = {}

def anti_spam(user_id):
    now = time.time()

    if user_id in LAST_MESSAGE:
        if now - LAST_MESSAGE[user_id] < 2:
            return False

    LAST_MESSAGE[user_id] = now
    return True

# =========================================
# حفظ مستخدم
# =========================================
def save_user(user):

    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id, name) VALUES (?, ?)",
        (user.id, user.first_name)
    )

    conn.commit()

# =========================================
# التحقق من الحظر
# =========================================
def is_banned(user_id):

    cursor.execute(
        "SELECT * FROM banned WHERE user_id=?",
        (user_id,)
    )

    return cursor.fetchone() is not None

# =========================================
# الاشتراك الإجباري
# =========================================
def check_sub(user_id):

    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False

# =========================================
# البيانات
# =========================================
DATA = {
    "tools": {
        "tsm_pro": (
            "⚙️ TSM Tool Pro",
            "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"
        ),

        "unlock_tool": (
            "🔓 UnlockTool",
            "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file"
        )
    },

    "drivers": {
        "adb": (
            "Adb Driver",
            "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"
        ),

        "mtk": (
            "MTK Driver",
            "https://www.mediafire.com/file_premium/0psu8awm57or6jj/drivers_mtk_v2.0.1.1_2.7z/file"
        )
    }
}

# =========================================
# القوائم
# =========================================
def build_menu(items: dict, back_callback: str):

    markup = types.InlineKeyboardMarkup(row_width=1)

    for key, value in items.items():

        markup.add(
            types.InlineKeyboardButton(
                value[0],
                callback_data=f"link_{key}"
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "🔙 رجوع",
            callback_data=back_callback
        )
    )

    return markup

# =========================================
# /start
# =========================================
@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id

    if is_banned(user_id):
        return

    if not anti_spam(user_id):
        return

    if not check_sub(user_id):

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "📢 اشترك بالقناة",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
            )
        )

        bot.send_message(
            message.chat.id,
            "⚠️ يجب الاشتراك بالقناة أولاً",
            reply_markup=markup
        )

        return

    save_user(message.from_user)

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "📦 قسم الأدوات",
            callback_data="main_tools"
        ),

        types.InlineKeyboardButton(
            "💾 قسم التعاريف",
            callback_data="main_drivers"
        ),

        types.InlineKeyboardButton(
            "📝 طلب أداة خاصة",
            callback_data="request_tool"
        )
    )

    bot.send_message(
        message.chat.id,
        (
            "👑 <b>مرحباً بك في HMAX Global System</b>\n\n"
            "نظام صيانة متكامل للأدوات والتعاريف"
        ),
        reply_markup=markup
    )

# =========================================
# لوحة الأدمن
# =========================================
@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("📊 الإحصائيات", "📢 إذاعة")
    markup.row("👥 المستخدمين", "🚫 حظر")

    bot.send_message(
        message.chat.id,
        "👨‍💻 لوحة تحكم الأدمن",
        reply_markup=markup
    )

# =========================================
# الإحصائيات
# =========================================
@bot.message_handler(func=lambda m: m.text == "📊 الإحصائيات")
def stats(message):

    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests")
    requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM banned")
    banned = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        (
            f"👥 المستخدمين: {users}\n"
            f"📝 الطلبات: {requests}\n"
            f"🚫 المحظورين: {banned}"
        )
    )

# =========================================
# الإذاعة
# =========================================
broadcast_mode = {}

@bot.message_handler(func=lambda m: m.text == "📢 إذاعة")
def broadcast_start(message):

    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return

    broadcast_mode[message.from_user.id] = True

    bot.send_message(
        message.chat.id,
        "✉️ أرسل رسالة الإذاعة"
    )

@bot.message_handler(func=lambda m: m.from_user.id in broadcast_mode)
def do_broadcast(message):

    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return

    text = message.text

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    sent = 0

    for user in users:

        try:
            bot.send_message(user[0], text)
            sent += 1

        except:
            pass

    del broadcast_mode[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ تم الإرسال إلى {sent} مستخدم"
    )

# =========================================
# الحظر
# =========================================
@bot.message_handler(func=lambda m: m.text == "🚫 حظر")
def ask_ban(message):

    if str(message.from_user.id) != ADMIN_CHAT_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "أرسل ID المستخدم"
    )

    bot.register_next_step_handler(msg, do_ban)

def do_ban(message):

    try:

        user_id = int(message.text)

        cursor.execute(
            "INSERT OR IGNORE INTO banned(user_id) VALUES(?)",
            (user_id,)
        )

        conn.commit()

        bot.send_message(
            message.chat.id,
            "✅ تم حظر المستخدم"
        )

    except:
        bot.send_message(
            message.chat.id,
            "❌ خطأ"
        )

# =========================================
# الأزرار
# =========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    try:

        if call.data == "main_tools":

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⚙️ اختر الأداة",
                reply_markup=build_menu(DATA["tools"], "back_start")
            )

        elif call.data == "main_drivers":

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="💾 اختر التعريف",
                reply_markup=build_menu(DATA["drivers"], "back_start")
            )

        elif call.data == "back_start":

            start(call.message)

        elif call.data.startswith("link_"):

            key = call.data.replace("link_", "")

            if key in DATA["tools"]:
                item = DATA["tools"][key]
                back_menu = "main_tools"

            else:
                item = DATA["drivers"][key]
                back_menu = "main_drivers"

            markup = types.InlineKeyboardMarkup()

            markup.add(
                types.InlineKeyboardButton(
                    "⬇️ تحميل مباشر",
                    url=item[1]
                )
            )

            markup.add(
                types.InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data=back_menu
                )
            )

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ <b>{item[0]}</b>",
                reply_markup=markup
            )

        elif call.data == "request_tool":

            msg = bot.send_message(
                call.message.chat.id,
                "📝 أرسل اسم الأداة المطلوبة"
            )

            bot.register_next_step_handler(
                msg,
                save_tool_request
            )

    except Exception as error:
        logging.error(error)

# =========================================
# حفظ الطلبات
# =========================================
def save_tool_request(message):

    try:

        text = message.text

        cursor.execute(
            "INSERT INTO requests(user_id, request) VALUES (?, ?)",
            (message.from_user.id, text)
        )

        conn.commit()

        if ADMIN_CHAT_ID != "0":

            bot.send_message(
                ADMIN_CHAT_ID,
                (
                    "📥 طلب جديد\n\n"
                    f"👤 {message.from_user.first_name}\n"
                    f"🆔 {message.from_user.id}\n\n"
                    f"📌 {text}"
                )
            )

        bot.reply_to(
            message,
            "✅ تم إرسال طلبك"
        )

    except Exception as error:

        logging.error(error)

        bot.reply_to(
            message,
            "❌ حدث خطأ"
        )

# =========================================
# التشغيل
# =========================================
if __name__ == "__main__":

    Thread(target=run_web).start()

    logging.info("Bot Started")

    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30
    )

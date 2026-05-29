
import os
import sqlite3
import logging
import time
from threading import Thread

from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

CHANNEL_USERNAME = "@hmaxpro"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route("/")
def home():
    return "HMAX PRO BOT ONLINE"

def run_web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

conn = sqlite3.connect("hmax_pro.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    points INTEGER DEFAULT 0,
    joined_by INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS banned(
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

DATA = {
    "tools": {
        "unlocktool": (
            "🔓 UnlockTool",
            "https://example.com"
        ),
        "umt": (
            "⚡ UMT Pro",
            "https://example.com"
        )
    }
}

LAST_MESSAGE = {}

def anti_spam(user_id):
    now = time.time()

    if user_id in LAST_MESSAGE:
        if now - LAST_MESSAGE[user_id] < 2:
            return False

    LAST_MESSAGE[user_id] = now
    return True

def save_user(user, ref=0):
    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id, name, joined_by) VALUES (?, ?, ?)",
        (user.id, user.first_name, ref)
    )
    conn.commit()

def add_points(user_id, amount):
    cursor.execute(
        "UPDATE users SET points = points + ? WHERE user_id=?",
        (amount, user_id)
    )
    conn.commit()

def get_points(user_id):
    cursor.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    return data[0] if data else 0

def is_banned(user_id):
    cursor.execute(
        "SELECT * FROM banned WHERE user_id=?",
        (user_id,)
    )

    return cursor.fetchone() is not None

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

    ref = 0

    if len(message.text.split()) > 1:

        data = message.text.split()[1]

        if data.startswith("ref_"):

            try:
                ref = int(data.replace("ref_", ""))

                if ref != user_id:
                    add_points(ref, 5)

            except:
                pass

    save_user(message.from_user, ref)

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "📦 الأدوات",
            callback_data="tools"
        ),

        types.InlineKeyboardButton(
            "🎁 نقاطي",
            callback_data="mypoints"
        ),

        types.InlineKeyboardButton(
            "👥 رابط الدعوة",
            callback_data="referral"
        ),

        types.InlineKeyboardButton(
            "📝 طلب أداة",
            callback_data="request_tool"
        )
    )

    bot.send_message(
        message.chat.id,
        "👑 أهلاً بك في HMAX PRO",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):

    if call.data == "tools":

        markup = types.InlineKeyboardMarkup()

        for key, item in DATA["tools"].items():

            markup.add(
                types.InlineKeyboardButton(
                    item[0],
                    url=item[1]
                )
            )

        bot.edit_message_text(
            "📦 أدوات الصيانة",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "mypoints":

        pts = get_points(call.from_user.id)

        bot.answer_callback_query(
            call.id,
            f"🎁 نقاطك: {pts}",
            show_alert=True
        )

    elif call.data == "referral":

        link = f"https://t.me/{bot.get_me().username}?start=ref_{call.from_user.id}"

        bot.send_message(
            call.message.chat.id,
            f"👥 رابط دعوتك:\n\n{link}"
        )

    elif call.data == "request_tool":

        msg = bot.send_message(
            call.message.chat.id,
            "📝 أرسل اسم الأداة"
        )

        bot.register_next_step_handler(
            msg,
            save_request
        )

def save_request(message):

    cursor.execute(
        "INSERT INTO requests(user_id, text) VALUES (?, ?)",
        (message.from_user.id, message.text)
    )

    conn.commit()

    if ADMIN_CHAT_ID:

        bot.send_message(
            ADMIN_CHAT_ID,
            f"📥 طلب جديد\n\n{message.text}"
        )

    bot.reply_to(
        message,
        "✅ تم إرسال الطلب"
    )

@bot.message_handler(commands=["stats"])
def stats(message):

    if message.from_user.id != ADMIN_CHAT_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests")
    requests = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,
        f"👥 المستخدمين: {users}\n📝 الطلبات: {requests}"
    )

if __name__ == "__main__":

    Thread(target=run_web).start()

    print("HMAX PRO STARTED")

    bot.infinity_polling(skip_pending=True)

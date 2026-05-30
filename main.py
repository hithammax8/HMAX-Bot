import os
import sqlite3
import logging
import time
from threading import Thread
from datetime import datetime

from flask import Flask
import telebot
from telebot import types

# ================= CONFIGURATION =================
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@yourchannel") # ضع يوزر قناتك هنا أو في المتغيرات

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# ================= WEB SERVER (RENDER) =================
@app.route("/")
def home():
    return "Haitham Max Tech Bot (HMAX PRO) is ONLINE"

def run_web():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= DATABASE =================
conn = sqlite3.connect("hmax_pro.db", check_same_thread=False)
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    points INTEGER DEFAULT 0,
    joined_by INTEGER DEFAULT 0,
    join_date TEXT
);
CREATE TABLE IF NOT EXISTS requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    req_date TEXT
);
CREATE TABLE IF NOT EXISTS banned(
    user_id INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS clicks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT,
    click_date TEXT
);
""")
conn.commit()

# ================= TOOLS DATA =================
DATA = {
    "tools": {
        "unlocktool": ("🔓 UnlockTool", "https://example.com"),
        "umt": ("⚡ UMT Pro", "https://example.com"),
        "iremoval": ("📱 iRemoval Pro (Official)", "https://example.com")
    }
}

LAST_MESSAGE = {}

# ================= FUNCTIONS =================
def anti_spam(user_id):
    now = time.time()
    if user_id in LAST_MESSAGE:
        if now - LAST_MESSAGE[user_id] < 1.5: # منع إرسال أكثر من رسالة خلال 1.5 ثانية
            return False
    LAST_MESSAGE[user_id] = now
    
    # تنظيف الذاكرة المؤقتة لمنع استهلاك الرام
    if len(LAST_MESSAGE) > 1000:
        LAST_MESSAGE.clear()
        LAST_MESSAGE[user_id] = now
    return True

def is_fake_user(user):
    if user.is_bot:
        return True
    if not user.first_name or user.first_name.strip() == "":
        return True
    return False

def check_sub(user_id):
    if CHANNEL_USERNAME == "@yourchannel" or not CHANNEL_USERNAME:
        return True # تخطي الفحص إذا لم يتم تعيين القناة
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Channel Check Error: {e}")
        return False

def add_points(user_id, amount):
    cursor.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def count_click(tool_name):
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO clicks(tool, click_date) VALUES (?, ?)", (tool_name, today))
    conn.commit()

# ================= START COMMAND =================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if is_fake_user(message.from_user):
        return
    
    cursor.execute("SELECT * FROM banned WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        return

    if not anti_spam(user_id):
        return

    # معالجة نظام الإحالة قبل التحقق من الاشتراك لتجنب ضياع النقاط
    ref = 0
    if len(message.text.split()) > 1:
        data = message.text.split()[1]
        if data.startswith("ref_"):
            try:
                parsed_ref = int(data.replace("ref_", ""))
                if parsed_ref != user_id:
                    ref = parsed_ref
            except:
                pass

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    is_new = cursor.fetchone() is None

    if is_new:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO users(user_id, name, joined_by, join_date) VALUES (?, ?, ?, ?)",
            (user_id, message.from_user.first_name, ref, today)
        )
        conn.commit()
        if ref != 0:
            add_points(ref, 5)

    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك بالقناة لتفعيل البوت", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
        bot.send_message(message.chat.id, "⚠️ <b>عذراً، يجب الاشتراك في قناة السيرفر الرسمية أولاً لتتمكن من استخدام البوت.</b>\n\nاضغط على الزر بالأسفل ثم أرسل /start مجدداً.", reply_markup=markup)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📦 الأدوات", callback_data="tools"),
        types.InlineKeyboardButton("📝 طلب أداة", callback_data="request_tool"),
        types.InlineKeyboardButton("🎁 نقاطي", callback_data="mypoints"),
        types.InlineKeyboardButton("👥 رابط الدعوة", callback_data="referral")
    )

    bot.send_message(message.chat.id, "👑 <b>أهلاً بك في سيرفر MaxTech (HMAX PRO)</b>\n\nاختر من القائمة أدناه:", reply_markup=markup)

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    if call.data == "tools":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, item in DATA["tools"].items():
            markup.add(types.InlineKeyboardButton(item[0], url=item[1]))
            count_click(item[0])

        bot.edit_message_text("📦 <b>أدوات الصيانة المتاحة:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "mypoints":
        cursor.execute("SELECT points FROM users WHERE user_id=?", (call.from_user.id,))
        pts = cursor.fetchone()
        points = pts[0] if pts else 0
        bot.answer_callback_query(call.id, f"🎁 إجمالي نقاطك هو: {points}", show_alert=True)

    elif call.data == "referral":
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start=ref_{call.from_user.id}"
        bot.send_message(call.message.chat.id, f"👥 <b>رابط الدعوة الخاص بك:</b>\n\n{link}\n\nشارك الرابط لزيادة نقاطك!")

    elif call.data == "request_tool":
        msg = bot.send_message(call.message.chat.id, "📝 <b>أرسل اسم الأداة أو الخدمة المطلوبة الآن:</b>")
        bot.register_next_step_handler(msg, save_request)

# ================= REQUESTS =================
def save_request(message):
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO requests(user_id, text, req_date) VALUES (?, ?, ?)", (message.from_user.id, message.text, today))
    conn.commit()

    if ADMIN_CHAT_ID != 0:
        bot.send_message(ADMIN_CHAT_ID, f"📥 <b>طلب جديد من</b> <code>{message.from_user.id}</code>:\n\n{message.text}")

    bot.reply_to(message, "✅ <b>تم إرسال طلبك للإدارة بنجاح.</b>")

# ================= DASHBOARD =================
@bot.message_handler(commands=["dashboard", "admin"])
def dashboard(message):
    if message.from_user.id != ADMIN_CHAT_ID:
        return

    today = datetime.now().strftime("%Y-%m-%d")

    # إحصائيات المستخدمين
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0] or 0

    # عدد المشتركين اليوم
    cursor.execute("SELECT COUNT(*) FROM users WHERE join_date=?", (today,))
    today_users = cursor.fetchone()[0] or 0

    # عدد الطلبات
    cursor.execute("SELECT COUNT(*) FROM requests")
    total_requests = cursor.fetchone()[0] or 0

    # عدد المحظورين
    cursor.execute("SELECT COUNT(*) FROM banned")
    total_banned = cursor.fetchone()[0] or 0

    # عداد النقرات
    cursor.execute("SELECT COUNT(*) FROM clicks")
    total_clicks = cursor.fetchone()[0] or 0

    # أفضل شخص دعى أعضاء
    cursor.execute("SELECT joined_by, COUNT(*) as total FROM users WHERE joined_by != 0 GROUP BY joined_by ORDER BY total DESC LIMIT 1")
    top_inviter_data = cursor.fetchone()
    if top_inviter_data:
        cursor.execute("SELECT name FROM users WHERE user_id=?", (top_inviter_data[0],))
        inviter_name = cursor.fetchone()
        inviter_name = inviter_name[0] if inviter_name else "مجهول"
        inviter_text = f"👤 {inviter_name} (أحضر {top_inviter_data[1]} أعضاء)"
    else:
        inviter_text = "لا يوجد"

    # أكثر أداة استخداماً
    cursor.execute("SELECT tool, COUNT(*) as total FROM clicks GROUP BY tool ORDER BY total DESC LIMIT 1")
    top_tool_data = cursor.fetchone()
    tool_text = f"🔥 {top_tool_data[0]} ({top_tool_data[1]} نقرة)" if top_tool_data else "لا يوجد"

    text = f"""
📊 <b>لوحة تحكم إدارة السيرفر (MaxTech)</b>

👥 <b>إحصائيات المستخدمين:</b> {total_users}
🆕 <b>عدد المشتركين اليوم:</b> {today_users}
🏆 <b>أفضل شخص دعى أعضاء:</b>
{inviter_text}

🔥 <b>أكثر أداة استخداماً:</b>
{tool_text}

📝 <b>عدد الطلبات:</b> {total_requests}
🚫 <b>عدد المحظورين:</b> {total_banned}
📈 <b>عداد النقرات الكلي:</b> {total_clicks}
"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("إرسال رسالة للكل", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("قائمة أفضل 10", callback_data="admin_top10")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_CHAT_ID:
        return
        
    if call.data == "admin_top10":
        cursor.execute("SELECT name, points FROM users ORDER BY points DESC LIMIT 10")
        data = cursor.fetchall()
        text = "🏆 <b>أفضل 10 مستخدمين:</b>\n\n"
        for i, user in enumerate(data, start=1):
            text += f"{i}- {user[0]} | 🎁 {user[1]} نقطة\n"
        bot.send_message(call.message.chat.id, text)
        
    elif call.data == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, "📢 <b>أرسل الرسالة التي تريد إذاعتها لجميع المستخدمين:</b>")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    sent = 0
    bot.send_message(message.chat.id, "⏳ <b>جاري الإرسال...</b>")
    for user in users:
        try:
            bot.send_message(user[0], message.text)
            sent += 1
            time.sleep(0.05) # تجنب حظر تيليجرام (Flood Limit)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ <b>تم الإرسال بنجاح إلى {sent} مستخدم.</b>")

# ================= RUN SERVER & BOT =================
if __name__ == "__main__":
    bot.remove_webhook() # تنظيف الـ Webhook لتجنب تعارض الـ Polling في Render
    Thread(target=run_web, daemon=True).start()
    logging.info("MaxTech Bot Started Successfully!")
    bot.infinity_polling(skip_pending=True)

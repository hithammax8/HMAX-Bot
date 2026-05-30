import telebot
from telebot import types
from flask import Flask
from threading import Thread
import sqlite3
from datetime import datetime, timedelta
import os

# 1. الإعدادات
TOKEN = "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU"
MY_CHAT_ID = "560330933"
CHANNEL_ID = "@haithamMax1"
bot = telebot.TeleBot(TOKEN)

# الحل الجذري لمشكلة 409 Conflict
bot.remove_webhook()

# قاعدة بيانات متكاملة (sqlite)
conn = sqlite3.connect("hmax_bot.db", check_same_thread=False)
cursor = conn.cursor()

# تحديث هيكل جدول المستخدمين وإضافة جداول جديدة
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, invited_by INTEGER, join_date TEXT, last_active TEXT, is_banned INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS tool_usage (user_id INTEGER, tool_name TEXT, timestamp TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS requests (user_id INTEGER, request_text TEXT, timestamp TEXT)")
conn.commit()

# تشغيل سيرفر الويب (للتوافق مع Render)
app = Flask(__name__)
@app.route("/")
def home(): return "HMAX System Active"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

Thread(target=run_flask).start()

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
    try: return bot.get_chat_member(CHANNEL_ID, user_id).status in ["member", "administrator", "creator"]
    except: return False

@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.is_bot: return
    
    # Handle referrals
    referred_by = None
    if message.text and len(message.text.split()) > 1:
        try: referred_by = int(message.text.split()[1])
        except ValueError: pass

    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (message.chat.id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        cursor.execute("INSERT INTO users (id, invited_by, join_date, last_active) VALUES (?, ?, ?, ?)", (message.chat.id, referred_by, today, today))
    else:
        cursor.execute("UPDATE users SET last_active = ? WHERE id = ?", (today, message.chat.id))
    conn.commit()

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("📝 طلب أداة", callback_data="req_tool"),
        types.InlineKeyboardButton("💎 نظام النقاط", callback_data="points_sys"),
        types.InlineKeyboardButton("📱 واتساب", url="https://wa.me/967772773388"),
        types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax")
    )
    bot.send_message(message.chat.id, "👑 أهلاً بك في HMAX Global System.", reply_markup=markup)

@bot.message_handler(commands=["dashboard"])
def dashboard(message):
    if str(message.chat.id) == MY_CHAT_ID:
        # إحصائيات المستخدمين
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        # عدد المشتركين اليوم (الذين انضموا اليوم)
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM users WHERE join_date = ?", (today,))
        new_users_today = cursor.fetchone()[0]

        # أفضل شخص دعى أعضاء
        cursor.execute("SELECT invited_by, COUNT(*) AS referrals FROM users WHERE invited_by IS NOT NULL GROUP BY invited_by ORDER BY referrals DESC LIMIT 1")
        top_referrer_data = cursor.fetchone()
        top_referrer = f"لا يوجد بعد" if not top_referrer_data else f"المستخدم ID: {top_referrer_data[0]} ({top_referrer_data[1]} دعوات)"

        # أكثر أداة استخداماً
        cursor.execute("SELECT tool_name, COUNT(*) AS usage_count FROM tool_usage GROUP BY tool_name ORDER BY usage_count DESC LIMIT 1")
        most_used_tool_data = cursor.fetchone()
        most_used_tool = f"لا يوجد بعد" if not most_used_tool_data else f"{most_used_tool_data[0]} ({most_used_tool_data[1]} استخدام)"

        # عدد الطلبات
        cursor.execute("SELECT COUNT(*) FROM requests")
        total_requests = cursor.fetchone()[0]

        # عدد المحظورين
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
        banned_users = cursor.fetchone()[0]

        # عداد النقرات (إجمالي جميع النقرات على الروابط)
        cursor.execute("SELECT SUM(clicks) FROM users")
        total_clicks = cursor.fetchone()[0] or 0

        dashboard_text = f"""
📊 **لوحة الإدارة**

👥 **إجمالي المستخدمين:** {total_users}
🆕 **مشتركون جدد اليوم:** {new_users_today}
🏆 **أفضل داعي:** {top_referrer}
🛠️ **الأداة الأكثر استخداماً:** {most_used_tool}
📝 **عدد الطلبات:** {total_requests}
🚫 **عدد المحظورين:** {banned_users}
🖱️ **إجمالي النقرات:** {total_clicks}

✅ النظام يعمل بكفاءة.
"""
        bot.reply_to(message, dashboard_text)
    else:
        bot.reply_to(message, "❌ للإدارة فقط.")

@bot.message_handler(commands=["ban"])
def ban_user(message):
    if str(message.chat.id) == MY_CHAT_ID:
        try:
            user_id_to_ban = int(message.text.split()[1])
            cursor.execute("UPDATE users SET is_banned = 1 WHERE id = ?", (user_id_to_ban,))
            conn.commit()
            bot.reply_to(message, f"✅ تم حظر المستخدم {user_id_to_ban}.")
        except (IndexError, ValueError):
            bot.reply_to(message, "❌ يرجى تحديد معرف المستخدم للحظر. مثال: /ban 123456789")
    else:
        bot.reply_to(message, "❌ للإدارة فقط.")

@bot.message_handler(commands=["unban"])
def unban_user(message):
    if str(message.chat.id) == MY_CHAT_ID:
        try:
            user_id_to_unban = int(message.text.split()[1])
            cursor.execute("UPDATE users SET is_banned = 0 WHERE id = ?", (user_id_to_unban,))
            conn.commit()
            bot.reply_to(message, f"✅ تم إلغاء حظر المستخدم {user_id_to_unban}.")
        except (IndexError, ValueError):
            bot.reply_to(message, "❌ يرجى تحديد معرف المستخدم لإلغاء الحظر. مثال: /unban 123456789")
    else:
        bot.reply_to(message, "❌ للإدارة فقط.")

@bot.message_handler(commands=["daily_new_users"])
def daily_new_users(message):
    if str(message.chat.id) == MY_CHAT_ID:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT id FROM users WHERE join_date = ?", (today,))
        new_users = cursor.fetchall()
        if new_users:
            user_ids_str = "\n".join([str(user[0]) for user in new_users])
            bot.reply_to(message, f"🆕 **المستخدمون الجدد اليوم ({today}):**\n{user_ids_str}")
        else:
            bot.reply_to(message, f"لا يوجد مستخدمون جدد اليوم ({today}).")
    else:
        bot.reply_to(message, "❌ للإدارة فقط.")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    # Check if user is banned
    cursor.execute("SELECT is_banned FROM users WHERE id = ?", (call.message.chat.id,))
    user_status = cursor.fetchone()
    if user_status and user_status[0] == 1:
        bot.answer_callback_query(call.id, "🚫 حسابك محظور ولا يمكنك استخدام البوت.", show_alert=True)
        return

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
        bot.edit_message_text(f"💎 نظام النقاط\nرابط دعوتك: {ref_link}", call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
    elif call.data.startswith("link_"):
        key = call.data.replace("link_", "")
        user_id = call.message.chat.id

        # Increment user clicks
        cursor.execute("UPDATE users SET clicks = clicks + 1 WHERE id = ?", (user_id,))
        conn.commit()

        # Log tool usage
        tool_name = DATA["tools"].get(key, (key,))[0] if key in DATA["tools"] else DATA["drivers"].get(key, (key,))[0]
        cursor.execute("INSERT INTO tool_usage (user_id, tool_name, timestamp) VALUES (?, ?, ?)", (user_id, tool_name, datetime.now().isoformat()))
        conn.commit()

        if is_subscribed(user_id):
            link = DATA["tools"].get(key, DATA["drivers"].get(key))[1]
            bot.edit_message_text(f"✅ الرابط:\n{link}", user_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start")))
        else:
            bot.answer_callback_query(call.id, "⚠️ اشترك في القناة أولاً!", show_alert=True)
    elif call.data == "req_tool":
        bot.edit_message_text("📝 أرسل اسم الأداة:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, lambda m: [
            cursor.execute("INSERT INTO requests (user_id, request_text, timestamp) VALUES (?, ?, ?)", (m.chat.id, m.text, datetime.now().isoformat())),
            conn.commit(),
            bot.send_message(MY_CHAT_ID, f"🔔 طلب جديد: {m.text}"), 
            bot.send_message(m.chat.id, "✅ تم إرسال الطلب!"), 
            start(m)
        ])

print("System is running...")
bot.infinity_polling()

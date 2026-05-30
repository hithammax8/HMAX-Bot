import telebot
from telebot import types
from flask import Flask
from threading import Thread
import sqlite3
from datetime import datetime
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

# تحديث هيكل الجداول
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, invited_by INTEGER, join_date TEXT, last_active TEXT, is_banned INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS tool_usage (user_id INTEGER, tool_name TEXT, timestamp TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS requests (user_id INTEGER, request_text TEXT, timestamp TEXT)")
conn.commit()

# تشغيل سيرفر الويب (للتوافق مع Render)
app = Flask(__name__)
@app.route("/")
def home(): return "HMAX System Active"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask).start()

# البيانات المحدثة مع الروابط الصحيحة
DATA = {
    "tools": {
        "tsm_pro": ("⚙️ TSM Tool Pro", "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"),
        "tsm_pro_edition": ("⚙️ TSM Pro Edition", "https://www.mediafire.com/file/j4d1v5wwoodbm4r/TSM+Pro+Edition+Setup[2026-05-28].7z/file"),
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

def get_start_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📦 قسم الأدوات", callback_data="main_tools"),
        types.InlineKeyboardButton("💾 قسم التعاريف", callback_data="main_drivers"),
        types.InlineKeyboardButton("📝 طلب أداة", callback_data="req_tool"),
        types.InlineKeyboardButton("💎 نظام النقاط", callback_data="points_sys"),
        types.InlineKeyboardButton("📱 واتساب", url="https://wa.me/967772773388"),
        types.InlineKeyboardButton("👨‍💻 تواصل معي", url="https://t.me/hithamMax")
    )
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.is_bot: return
    
    referred_by = None
    if message.text and len(message.text.split()) > 1:
        try: referred_by = int(message.text.split()[1])
        except ValueError: pass

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT id FROM users WHERE id = ?", (message.chat.id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id, invited_by, join_date, last_active) VALUES (?, ?, ?, ?)", (message.chat.id, referred_by, today, today))
    else:
        cursor.execute("UPDATE users SET last_active = ? WHERE id = ?", (today, message.chat.id))
    conn.commit()

    bot.send_message(message.chat.id, "👑 أهلاً بك في HMAX Global System.", reply_markup=get_start_markup())

@bot.message_handler(commands=["dashboard"])
def dashboard(message):
    if str(message.chat.id) == MY_CHAT_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM users WHERE join_date = ?", (today,))
        new_users_today = cursor.fetchone()[0]
        cursor.execute("SELECT invited_by, COUNT(*) AS referrals FROM users WHERE invited_by IS NOT NULL GROUP BY invited_by ORDER BY referrals DESC LIMIT 1")
        top_referrer_data = cursor.fetchone()
        top_referrer = f"لا يوجد" if not top_referrer_data else f"{top_referrer_data[0]} ({top_referrer_data[1]})"
        cursor.execute("SELECT tool_name, COUNT(*) AS usage_count FROM tool_usage GROUP BY tool_name ORDER BY usage_count DESC LIMIT 1")
        most_used_tool_data = cursor.fetchone()
        most_used_tool = f"لا يوجد" if not most_used_tool_data else f"{most_used_tool_data[0]}"
        cursor.execute("SELECT COUNT(*) FROM requests")
        total_requests = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
        banned_users = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(clicks) FROM users")
        total_clicks = cursor.fetchone()[0] or 0

        text = f"""📊 **لوحة الإدارة**
👥 إجمالي المستخدمين: {total_users}
🆕 مشتركين جدد اليوم: {new_users_today}
🏆 أفضل داعي: {top_referrer}
🛠️ الأكثر استخداماً: {most_used_tool}
📝 عدد الطلبات: {total_requests}
🚫 المحظورين: {banned_users}
🖱️ إجمالي النقرات: {total_clicks}"""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_start"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.reply_to(message, "❌ للإدارة فقط.")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cursor.execute("SELECT is_banned FROM users WHERE id = ?", (call.message.chat.id,))
    res = cursor.fetchone()
    if res and res[0] == 1:
        bot.answer_callback_query(call.id, "🚫 حسابك محظور.", show_alert=True)
        return

    if call.data == "back_start":
        bot.edit_message_text("👑 أهلاً بك في HMAX Global System.", call.message.chat.id, call.message.message_id, reply_markup=get_start_markup())
    
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
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
        bot.edit_message_text(f"💎 نظام النقاط\nرابط دعوتك: {ref_link}", call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif call.data.startswith("link_"):
        key = call.data.replace("link_", "")
        user_id = call.message.chat.id
        cursor.execute("UPDATE users SET clicks = clicks + 1 WHERE id = ?", (user_id,))
        tool_name = DATA["tools"].get(key, DATA["drivers"].get(key, (key,)))[0]
        cursor.execute("INSERT INTO tool_usage (user_id, tool_name, timestamp) VALUES (?, ?, ?)", (user_id, tool_name, datetime.now().isoformat()))
        conn.commit()

        if is_subscribed(user_id):
            link = DATA["tools"].get(key, DATA["drivers"].get(key))[1]
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_start"))
            bot.edit_message_text(f"✅ الرابط:\n{link}", user_id, call.message.message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "⚠️ اشترك في القناة أولاً!", show_alert=True)
            
    elif call.data == "req_tool":
        bot.edit_message_text("📝 أرسل اسم الأداة:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, lambda m: [
            cursor.execute("INSERT INTO requests (user_id, request_text, timestamp) VALUES (?, ?, ?)", (m.chat.id, m.text, datetime.now().isoformat())),
            conn.commit(),
            bot.send_message(MY_CHAT_ID, f"🔔 طلب جديد: {m.text}"), 
            bot.send_message(m.chat.id, "✅ تم إرسال الطلب!"), 
            bot.send_message(m.chat.id, "👑 أهلاً بك في HMAX Global System.", reply_markup=get_start_markup())
        ])

print("System is running...")
bot.infinity_polling()

import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# ==============================================================================
# 1. الإعدادات والثوابت
# ==============================================================================

# استخدام متغيرات البيئة للتوكن ومعرفات الدردشة لزيادة الأمان والمرونة
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8621204418:AAHkLlUefZTY8JaY4rFain_qqniwzBWRAmU")
MY_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "560330933")
CHANNEL_ID = os.getenv("CHANNEL_USERNAME", "@haithamMax1")

bot = telebot.TeleBot(TOKEN)

# نظام إحصائيات داخلي بسيط
stats = {"users": 0, "clicks": 0, "requests": 0, "blocked": 0}

# تعريفات الأزرار والبيانات
CALLBACK_PREFIX_LINK = "link_"
CALLBACK_MAIN_TOOLS = "main_tools"
CALLBACK_MAIN_DRIVERS = "main_drivers"
CALLBACK_REQ_TOOL = "req_tool"
CALLBACK_BACK_START = "back_start"
CALLBACK_SIGMA_OPTIONS = "sigma_options"

# قاعدة بيانات الأدوات والتعاريف
# يمكن نقل هذه البيانات إلى ملف JSON خارجي لتحسين المرونة وسهولة التحديث
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

# ==============================================================================
# 2. وظائف مساعدة
# ==============================================================================

def is_subscribed(user_id: int) -> bool:
    """التحقق مما إذا كان المستخدم مشتركًا في القناة المحددة."""
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiException as e:
        # التعامل مع الأخطاء المحتملة من API تيليجرام، مثل عدم وجود القناة
        print(f"Error checking subscription for user {user_id} in channel {CHANNEL_ID}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking subscription: {e}")
        return False

def create_inline_keyboard(buttons: list[tuple[str, str]], row_width: int = 1) -> types.InlineKeyboardMarkup:
    """إنشاء لوحة مفاتيح داخلية (Inline Keyboard) من قائمة أزرار."""
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    for text, callback_data in buttons:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    return markup

def create_url_keyboard(buttons: list[tuple[str, str]], row_width: int = 1) -> types.InlineKeyboardMarkup:
    """إنشاء لوحة مفاتيح داخلية (Inline Keyboard) من قائمة أزرار URL."""
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    for text, url in buttons:
        markup.add(types.InlineKeyboardButton(text, url=url))
    return markup

# ==============================================================================
# 3. معالجات الأوامر والرسائل
# ==============================================================================

@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    """معالج أمر /start: يرحب بالمستخدم ويعرض الأزرار الرئيسية."""
    stats["users"] += 1
    buttons = [
        ("📦 قسم الأدوات", CALLBACK_MAIN_TOOLS),
        ("💾 قسم التعاريف", CALLBACK_MAIN_DRIVERS),
        ("📝 طلب أداة", CALLBACK_REQ_TOOL),
    ]
    url_buttons = [
        ("📢 قناة الأخبار", f"https://t.me/{CHANNEL_ID.replace('@', '')}"),
        ("📱 واتساب", "https://wa.me/967772773388"),
        ("👨‍💻 تواصل معي", "https://t.me/hithamMax")
    ]
    
    markup = create_inline_keyboard(buttons)
    markup.add(*create_url_keyboard(url_buttons).keyboard[0]) # دمج أزرار الـ URL

    bot.send_message(message.chat.id, "👑 أهلاً بك في HMAX Global System.", reply_markup=markup)

@bot.message_handler(commands=['dashboard'])
def dashboard_command(message: types.Message):
    """معالج أمر /dashboard: يعرض إحصائيات البوت للمشرف فقط."""
    if str(message.chat.id) == MY_CHAT_ID:
        text = (
            "📊 **لوحة تحكم إدارة السيرفر المتقدمة**\n\n"
            f"👥 إجمالي المستخدمين: {stats['users']}\n"
            f"🖱️ عدد النقرات الكلي: {stats['clicks']}\n"
            f"📝 عدد الطلبات المرسلة: {stats['requests']}\n"
            f"🚫 عدد المحظورين: {stats['blocked']}\n\n"
            "✅ النظام يعمل بكفاءة."
        )
        bot.reply_to(message, text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ هذه الأوامر للإدارة فقط.")

# ==============================================================================
# 4. معالجات الاستدعاءات (Callback Queries)
# ==============================================================================

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call: types.CallbackQuery):
    """معالج جميع استدعاءات الأزرار الداخلية."""
    stats["clicks"] += 1
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == CALLBACK_BACK_START:
        start_command(call.message)
    elif call.data == CALLBACK_MAIN_TOOLS:
        buttons = [
            ("⚙️ TSM Tool Pro", f"{CALLBACK_PREFIX_LINK}tsm_pro"),
            ("⚡ DFT Pro Tool", f"{CALLBACK_PREFIX_LINK}dft_pro"),
            ("🔋 Sigma Plus (الخيارات)", CALLBACK_SIGMA_OPTIONS),
            ("🔓 UnlockTool", f"{CALLBACK_PREFIX_LINK}unlock_tool"),
            ("🔙 رجوع", CALLBACK_BACK_START)
        ]
        markup = create_inline_keyboard(buttons)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⚙️ اختر الأداة:", reply_markup=markup)
    elif call.data == CALLBACK_SIGMA_OPTIONS:
        buttons = []
        for k in ["sigma_main", "sigma_kirin", "sigma_exynos"]:
            buttons.append((DATA["tools"][k][0], f"{CALLBACK_PREFIX_LINK}{k}"))
        buttons.append(("🔙 رجوع للأدوات", CALLBACK_MAIN_TOOLS))
        markup = create_inline_keyboard(buttons)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🔋 خيارات Sigma:", reply_markup=markup)
    elif call.data == CALLBACK_MAIN_DRIVERS:
        buttons = []
        for k, v in DATA["drivers"].items():
            buttons.append((v[0], f"{CALLBACK_PREFIX_LINK}{k}"))
        buttons.append(("🔙 رجوع", CALLBACK_BACK_START))
        markup = create_inline_keyboard(buttons)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="💾 اختر التعريف:", reply_markup=markup)
    elif call.data.startswith(CALLBACK_PREFIX_LINK):
        key = call.data.replace(CALLBACK_PREFIX_LINK, "")
        if is_subscribed(chat_id):
            # البحث في الأدوات أولاً، ثم في التعاريف
            item_data = DATA["tools"].get(key) or DATA["drivers"].get(key)
            if item_data:
                link = item_data[1]
                markup = create_inline_keyboard([("🔙 رجوع", CALLBACK_BACK_START)])
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"✅ الرابط:\n{link}", reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "⚠️ لم يتم العثور على العنصر المطلوب.", show_alert=True)
        else:
            stats["blocked"] += 1
            bot.answer_callback_query(call.id, "⚠️ اشترك في القناة أولاً!", show_alert=True)
    elif call.data == CALLBACK_REQ_TOOL:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="📝 أرسل اسم الأداة:")
        bot.register_next_step_handler(call.message, process_tool_request)

def process_tool_request(message: types.Message):
    """معالج لطلب أداة من المستخدم."""
    stats["requests"] += 1
    bot.send_message(MY_CHAT_ID, f"🔔 طلب جديد من {message.from_user.first_name}:\n{message.text}")
    bot.send_message(message.chat.id, "✅ تم إرسال طلبك للإدارة بنجاح!")
    start_command(message)

# ==============================================================================
# 5. سيرفر الويب (لضمان بقاء البوت حياً)
# ==============================================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "HMAX System is running!"

def run_flask_app():
    app.run(host='0.0.0.0', port=os.getenv("PORT", 8080))

# ==============================================================================
# 6. نقطة الدخول الرئيسية
# ==============================================================================

if __name__ == '__main__':
    print("Starting Flask web server...")
    Thread(target=run_flask_app).start()
    print("Starting Telegram bot polling...")
    bot.infinity_polling()


import os
import logging
from threading import Thread

from flask import Flask
import telebot
from telebot import types

# =========================================
# إعدادات البوت
# =========================================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not TOKEN:
    raise ValueError("يرجى إضافة BOT_TOKEN داخل متغيرات البيئة")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# =========================================
# تشغيل Flask لإبقاء الخدمة فعالة
# =========================================
app = Flask(__name__)

@app.route("/")
def home():
    return "HMAX System is running!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# =========================================
# البيانات
# =========================================
DATA = {
    "tools": {
        "tsm_pro": (
            "⚙️ TSM Tool Pro",
            "https://www.mediafire.com/file/vqh1h1uhwq9s2xo/TSM_SetupV2.4.1.7z/file"
        ),
        "tsm_edition": (
            "🔧 TSM Pro Edition",
            "https://www.mediafire.com/file/j4d1v5wwoodbm4r/TSM+Pro+Edition+Setup%5B2026-05-28%5D.7z/file"
        ),
        "unlock_tool": (
            "🔓 UnlockTool",
            "https://www.mediafire.com/file_premium/5r2bzw8dr67cyh5/UnlockTool-2026-05-29-0.zip/file"
        ),
        "dft_pro": (
            "⚡ DFT Pro Tool",
            "https://www.mediafire.com/file/afpqr6duvxavdjf/DFTPRO_v7.0.7.exe/file"
        ),
        "sigma": (
            "🔋 Sigma Plus",
            "https://sigmakey.com/nfs/content/5802/file/sigmaplus-software-setup-v1.01.11.ehe"
        )
    },

    "drivers": {
        "adb": (
            "Adb Driver",
            "https://www.mediafire.com/file_premium/yx9pry29zxw0rsd/UniversalAdbDriverSetup.msi/file"
        ),
        "qcom_mtk": (
            "Univ. QCOM-MTK-ADB",
            "https://www.mediafire.com/file_premium/ko4na2ox2rcytbc/generic_usb_driver%257BQLM-MTK-ADB%257Dv1.1.0.zip/file"
        ),
        "mtk": (
            "MTK Driver",
            "https://www.mediafire.com/file_premium/0psu8awm57or6jj/drivers_mtk_v2.0.1.1_2.7z/file"
        ),
        "samsung": (
            "Samsung All USB",
            "https://www.mediafire.com/file_premium/92yzwgkkvkutye5/SAMSUNG_USB_Driver_for_Mobile_Phones_3.exe/file"
        ),
        "fastboot": (
            "FASTBOOT DRIVER",
            "https://mega.nz/file/w0plHSKZ#TjvkWuc9OmOpQiJq7Nr0U-ANlPVyf7RP1-2KvcgaSO4"
        ),
        "exynos": (
            "Exynos driver",
            "https://mega.nz/file/ksYGmJ6T#_7DeakMDKI9lPkGIvUA0TIN9qHGCUtSrDfTDAump3WU"
        ),
        "adb_fix": (
            "حل مشكلة ADB",
            "https://mega.nz/file/UgZwSCRS#rgIJ8Wdli6yG_m6V7aWzJZmrVLIfHTrzQWZUhvU6Ums"
        )
    }
}

# =========================================
# أدوات مساعدة
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
        ),

        types.InlineKeyboardButton(
            "📢 قناة الأخبار",
            url="https://t.me/haithamMax1"
        ),

        types.InlineKeyboardButton(
            "👨‍💻 تواصل معي",
            url="https://t.me/hithamMax"
        )
    )

    bot.send_message(
        message.chat.id,
        (
            "👑 <b>مرحباً بك في HMAX Global System</b>\n\n"
            "نظام صيانة متكامل للأدوات والتعاريف."
        ),
        reply_markup=markup
    )

# =========================================
# معالجة الأزرار
# =========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    try:

        if call.data == "back_start":
            start(call.message)
            return

        if call.data == "main_tools":

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="⚙️ اختر الأداة المطلوبة:",
                reply_markup=build_menu(DATA["tools"], "back_start")
            )
            return

        if call.data == "main_drivers":

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="💾 اختر التعريف المطلوب:",
                reply_markup=build_menu(DATA["drivers"], "back_start")
            )
            return

        if call.data.startswith("link_"):

            key = call.data.replace("link_", "")

            if key in DATA["tools"]:
                item = DATA["tools"][key]
                back_menu = "main_tools"

            elif key in DATA["drivers"]:
                item = DATA["drivers"][key]
                back_menu = "main_drivers"

            else:
                bot.answer_callback_query(
                    call.id,
                    "العنصر غير موجود"
                )
                return

            markup = types.InlineKeyboardMarkup(row_width=1)

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

            return

        if call.data == "request_tool":

            msg = bot.send_message(
                call.message.chat.id,
                "📝 أرسل اسم الأداة المطلوبة:"
            )

            bot.register_next_step_handler(
                msg,
                save_tool_request
            )

    except Exception as error:
        logging.error(error)

def save_tool_request(message):

    try:

        text = message.text.strip()

        if ADMIN_CHAT_ID:

            bot.send_message(
                ADMIN_CHAT_ID,
                (
                    "📥 طلب أداة جديدة\n\n"
                    f"👤 المستخدم: {message.from_user.first_name}\n"
                    f"🆔 ID: {message.from_user.id}\n\n"
                    f"📌 الطلب:\n{text}"
                )
            )

        bot.reply_to(
            message,
            "✅ تم إرسال طلبك للإدارة."
        )

    except Exception as error:
        logging.error(error)
        bot.reply_to(
            message,
            "❌ حدث خطأ أثناء إرسال الطلب."
        )

# =========================================
# تشغيل النظام
# =========================================
if __name__ == "__main__":

    Thread(target=run_web).start()

    logging.info("Bot started...")

    bot.infinity_polling(
        timeout=30,

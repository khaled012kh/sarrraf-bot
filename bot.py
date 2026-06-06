"""
🤖 بوت صرّاف - محول العملات الذكي
Telegram Currency Converter Bot
- يدعم 161+ عملة عالمية
- تحديث تلقائي للأسعار كل ساعة
- واجهة عربية بالكامل
- بدون مفتاح API
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ====================== الإعدادات ======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8928361588:AAHkkxvEcYjJw9ZyLha9gqLsiAXpvMGTHNM")
# مفتاح API اختياري - لو مش موجود بنستخدم المصدر المجاني العام
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "")
RATES_FILE = Path("rates_cache.json")
UPDATE_INTERVAL = 3600  # تحديث كل ساعة بالثواني

# رابطين: واحد بمفتاح، وواحد مجاني
PRIMARY_API_URL = "https://v6.exchangerate-api.com/v6/{key}/latest/USD"
FREE_API_URL = "https://open.er-api.com/v6/latest/USD"

# الحالات (States) للمحادثة
SELECT_FROM, SELECT_TO, ENTER_AMOUNT = range(3)

# ====================== تسجيل الأحداث ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ====================== رموز العملات الشائعة ======================
CURRENCY_FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
    "SAR": "🇸🇦", "AED": "🇦🇪", "EGP": "🇪🇬", "KWD": "🇰🇼",
    "QAR": "🇶🇦", "BHD": "🇧🇭", "OMR": "🇴🇲", "JOD": "🇯🇴",
    "LBP": "🇱🇧", "IQD": "🇮🇶", "MAD": "🇲🇦", "TND": "🇹🇳",
    "DZD": "🇩🇿", "LYD": "🇱🇾", "SDG": "🇸🇩", "CNY": "🇨🇳",
    "INR": "🇮🇳", "PKR": "🇵🇰", "TRY": "🇹🇷", "IRR": "🇮🇷",
    "RUB": "🇷🇺", "CAD": "🇨🇦", "AUD": "🇦🇺", "CHF": "🇨🇭",
    "BRL": "🇧🇷", "MXN": "🇲🇽", "ZAR": "🇿🇦", "NGN": "🇳🇬",
    "BTC": "₿",
}

CURRENCY_NAMES_AR = {
    "USD": "الدولار الأمريكي", "EUR": "اليورو", "GBP": "الجنيه الإسترليني",
    "JPY": "الين الياباني", "SAR": "الريال السعودي", "AED": "الدرهم الإماراتي",
    "EGP": "الجنيه المصري", "KWD": "الدينار الكويتي", "QAR": "الريال القطري",
    "BHD": "الدينار البحريني", "OMR": "الريال العماني", "JOD": "الدينار الأردني",
    "LBP": "الجنيه اللبناني", "IQD": "الدينار العراقي", "MAD": "الدرهم المغربي",
    "TND": "الدينار التونسي", "DZD": "الدينار الجزائري", "LYD": "الدينار الليبي",
    "SDG": "الجنيه السوداني", "CNY": "اليوان الصيني", "INR": "الروبية الهندية",
    "PKR": "الروبية الباكستانية", "TRY": "الليرة التركية", "IRR": "الريال الإيراني",
    "RUB": "الروبل الروسي", "CAD": "الدولار الكندي", "AUD": "الدولار الأسترالي",
    "CHF": "الفرنك السويسري", "BRL": "الريال البرازيلي", "MXN": "البيسو المكسيكي",
    "ZAR": "الراند الجنوب أفريقي", "NGN": "النايرا النيجيري", "BTC": "بيتكوين",
}

# ====================== دوال الأسعار ======================
def load_rates() -> dict:
    """تحميل الأسعار من الكاش المحلي"""
    if RATES_FILE.exists():
        try:
            with open(RATES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في قراءة ملف الأسعار: {e}")
    return {}


def save_rates(data: dict) -> None:
    """حفظ الأسعار في الكاش المحلي"""
    try:
        with open(RATES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"خطأ في حفظ ملف الأسعار: {e}")


def get_currency_emoji(code: str) -> str:
    return CURRENCY_FLAGS.get(code, "💱")


def get_currency_name(code: str) -> str:
    return CURRENCY_NAMES_AR.get(code, code)


def convert(amount: float, from_cur: str, to_cur: str, rates: dict) -> float | None:
    """تحويل العملة باستخدام الأسعار المخزنة (مقارنة بـ USD)"""
    try:
        # كل الأسعار في API تكون بـ USD كقاعدة
        if from_cur == "USD":
            rate = rates.get(to_cur)
        elif to_cur == "USD":
            rate = 1 / rates.get(from_cur, 1)
        else:
            from_rate = rates.get(from_cur, 1)
            to_rate = rates.get(to_cur, 1)
            rate = to_rate / from_rate
        return round(amount * rate, 4) if rate else None
    except Exception as e:
        logger.error(f"خطأ في التحويل: {e}")
        return None


# ====================== تحديث الأسعار التلقائي ======================
async def update_rates_job(context: ContextTypes.DEFAULT_TYPE):
    """مهمة دورية لتحديث الأسعار - مجاني 100%"""
    import aiohttp
    # لو فيه مفتاح نستخدم الـ API الرسمي، لو مفيش نستخدم المجاني العام
    if EXCHANGE_API_KEY and EXCHANGE_API_KEY != "PUT_YOUR_EXCHANGE_RATE_API_KEY_HERE":
        url = PRIMARY_API_URL.format(key=EXCHANGE_API_KEY)
    else:
        url = FREE_API_URL

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                data = await resp.json()
                # المصدر المجاني بيرجع "result": "success" + rates مباشرة
                # المصدر الرسمي بيرجع "result": "success" + conversion_rates
                if data.get("result") == "success" or "rates" in data:
                    rates_data = data.get("conversion_rates") or data.get("rates", {})
                    payload = {
                        "rates": rates_data,
                        "last_update": data.get("time_last_update_unix", 0) or data.get("time_last_update", 0),
                        "next_update": data.get("time_next_update_unix", 0) or data.get("time_next_update", 0),
                        "base": "USD",
                    }
                    save_rates(payload)
                    logger.info(f"✅ تم تحديث أسعار العملات - {len(rates_data)} عملة")
                else:
                    logger.error(f"❌ فشل التحديث: {data.get('error-type', 'unknown error')}")
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث الأسعار: {e}")


# ====================== لوحة المفاتيح ======================
def build_currency_keyboard(page: int = 0, mode: str = "from") -> InlineKeyboardMarkup:
    """إنشاء لوحة اختيار العملة مع ترقيم الصفحات"""
    rates = load_rates()
    currencies = sorted(rates.get("rates", {}).keys()) if rates else sorted(CURRENCY_FLAGS.keys())
    # لو مفيش rates متاحة، نستخدم قائمة افتراضية شائعة
    if not currencies:
        currencies = sorted(CURRENCY_FLAGS.keys())

    # عرض 30 عملة في كل صفحة (3 أعمدة × 10 صفوف)
    per_page = 30
    start = page * per_page
    end = start + per_page
    page_currencies = currencies[start:end]
    total_pages = (len(currencies) + per_page - 1) // per_page

    buttons = []
    row = []
    for i, code in enumerate(page_currencies):
        flag = get_currency_emoji(code)
        row.append(
            InlineKeyboardButton(
                f"{flag} {code}",
                callback_data=f"cur_{mode}_{code}_p{page}"
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # أزرار التنقل بين الصفحات
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"page_{mode}_{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"page_{mode}_{page+1}"))
    buttons.append(nav)
    buttons.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])

    return InlineKeyboardMarkup(buttons)


def build_main_keyboard() -> ReplyKeyboardMarkup:
    """لوحة المفاتيح الرئيسية الدائمة"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💱 تحويل سريع"), KeyboardButton("💰 أسعار العملات")],
            [KeyboardButton("📊 عملات شائعة"), KeyboardButton("ℹ️ المساعدة")],
        ],
        resize_keyboard=True,
    )


# ====================== أوامر البوت ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rates = load_rates()
    last_update = "غير معروف"
    if rates and rates.get("last_update"):
        last_update = datetime.fromtimestamp(rates["last_update"]).strftime("%Y-%m-%d %H:%M")

    welcome = (
        f"👋 أهلاً **{user.first_name}** في **صرّاف**!\n\n"
        "💱 محول عملات ذكي وسريع\n"
        f"🌍 عدد العملات المتاحة: **{len(rates.get('rates', {}))}** عملة\n"
        f"🕐 آخر تحديث للأسعار: **{last_update}**\n\n"
        "**اختار من الأزرار تحت:**\n"
        "• 💱 **تحويل سريع** - حوّل بين أي عملتين\n"
        "• 💰 **أسعار العملات** - شوف أسعار أي عملة\n"
        "• 📊 **عملات شائعة** - أشهر العملات الآن\n"
        "• ℹ️ **المساعدة** - طريقة الاستخدام\n\n"
        "✨ **أوامر سريعة:**\n"
        "`/convert` • `/rates USD` • `/popular`\n"
        "أو ابعتلي: `100 USD to EGP`\n\n"
        "🔄 التحديث التلقائي كل ساعة"
    )
    await update.message.reply_text(welcome, reply_markup=build_main_keyboard(), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 **دليل استخدام صرّاف:**\n\n"
        "**1️⃣ طريقة سريعة (الأفضل):**\n"
        "ابعتلي رسالة بالشكل ده:\n"
        "`100 USD to EGP`\n"
        "`50 EUR to SAR`\n"
        "`1000 JPY to AED`\n\n"
        "**2️⃣ طريقة تفاعلية:**\n"
        "`/convert` أو اضغط «💱 تحويل سريع»\n"
        "اختار العملة ➜ اختار العملة ➜ ادخل المبلغ\n\n"
        "**3️⃣ عرض أسعار عملة:**\n"
        "`/rates USD` يعرض سعر الدولار\n"
        "`/rates EGP` يعرض سعر الجنيه المصري\n\n"
        "**4️⃣ أشهر العملات:**\n"
        "`/popular` يعرض أهم 10 عملات\n\n"
        "💡 **نصائح:**\n"
        "• الأسعار بتتحدث كل ساعة أوتوماتيك\n"
        "• البوت بيدعم 161+ عملة عالمية\n"
        "• ابعت المبلغ بأي صيغة: `100` أو `100.5` أو `1,000`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 **اختار العملة اللي عايز تحوّل منها:**",
        reply_markup=build_currency_keyboard(0, "from"),
        parse_mode="Markdown",
    )
    return SELECT_FROM


async def from_currency_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel":
        await query.edit_message_text("❌ تم الإلغاء")
        return ConversationHandler.END

    if query.data.startswith("page_"):
        # تنقل بين الصفحات
        _, mode, page = query.data.split("_")
        await query.edit_message_reply_markup(
            build_currency_keyboard(int(page), mode)
        )
        return SELECT_FROM

    _, mode, currency, page = query.data.split("_")
    context.user_data["from_currency"] = currency
    await query.edit_message_text(
        f"✅ المصدر: **{get_currency_emoji(currency)} {currency}**\n\n"
        f"💱 دلوقتي اختار العملة اللي عايز تحوّل **إليها:**",
        reply_markup=build_currency_keyboard(0, "to"),
        parse_mode="Markdown",
    )
    return SELECT_TO


async def to_currency_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel":
        await query.edit_message_text("❌ تم الإلغاء")
        return ConversationHandler.END

    if query.data.startswith("page_"):
        _, mode, page = query.data.split("_")
        await query.edit_message_reply_markup(
            build_currency_keyboard(int(page), mode)
        )
        return SELECT_TO

    _, mode, currency, page = query.data.split("_")
    context.user_data["to_currency"] = currency
    await query.edit_message_text(
        f"✅ المصدر: **{context.user_data['from_currency']}**\n"
        f"✅ الهدف: **{get_currency_emoji(currency)} {currency}**\n\n"
        "💵 دلوقتي ابعت **المبلغ** اللي عايز تحوّلو:",
        parse_mode="Markdown",
    )
    return ENTER_AMOUNT


async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(",", ".").strip())
    except ValueError:
        await update.message.reply_text("❌ يا ريس ابعت رقم صحيح، مثلاً: 100")
        return ENTER_AMOUNT

    from_cur = context.user_data["from_currency"]
    to_cur = context.user_data["to_currency"]
    rates = load_rates().get("rates", {})

    if not rates:
        await update.message.reply_text(
            "⚠️ مفيش أسعار متاحة دلوقتي. استنى دقيقة وجرب تاني،"
            " أو تأكد إن الـ API key متظبوط."
        )
        return ConversationHandler.END

    result = convert(amount, from_cur, to_cur, rates)
    if result is None:
        await update.message.reply_text("❌ حصلت مشكلة في التحويل. جرب تاني.")
        return ConversationHandler.END

    # النتيجة
    from_name = get_currency_name(from_cur)
    to_name = get_currency_name(to_cur)
    rate = result / amount if amount else 0
    text = (
        f"💱 **نتيجة التحويل:**\n\n"
        f"`{amount:,.2f}` **{from_cur}** ({from_name})\n"
        f"⬇️\n"
        f"`{result:,.4f}` **{to_cur}** ({to_name})\n\n"
        f"📊 **سعر الصرف:** 1 {from_cur} = `{rate:,.4f}` {to_cur}\n"
        f"🕐 آخر تحديث: `{datetime.fromtimestamp(load_rates()['last_update']).strftime('%Y-%m-%d %H:%M')}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=build_main_keyboard())
    context.user_data.clear()
    return ConversationHandler.END


# ====================== تحويل سريع بالنص ======================
async def quick_convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحويل سريع من نص: 100 USD to EGP"""
    text = update.message.text.strip().upper()
    # تجاهل أزرار القائمة
    if text in ["💱 تحويل سريع", "💰 أسعار العملات", "📊 عملات شائعة", "ℹ️ المساعدة"]:
        if text == "💱 تحويل سريع":
            return await convert_command(update, context)
        elif text == "ℹ️ المساعدة":
            return await help_command(update, context)
        elif text == "💰 أسعار العملات":
            await update.message.reply_text(
                "ابعتلي الأمر بالشكل ده:\n`/rates USD`\n"
                "وهيتم عرض سعر العملة أمام باقي العملات.",
                parse_mode="Markdown",
            )
            return
        elif text == "📊 عملات شائعة":
            return await popular_currencies(update, context)

    # محاولة استخراج: 100 USD to EGP
    import re
    match = re.match(r"^([\d.,]+)\s*([A-Z]{3})\s*(?:TO|في|إلي|الى|->|=>)\s*([A-Z]{3})$", text)
    if not match:
        await update.message.reply_text(
            "❓ مش فاهم. ابعت بالشكل ده:\n"
            "`100 USD to EGP`",
            parse_mode="Markdown",
        )
        return

    amount_str, from_cur, to_cur = match.groups()
    try:
        amount = float(amount_str.replace(",", "."))
    except ValueError:
        await update.message.reply_text("❌ المبلغ غلط")
        return

    rates = load_rates().get("rates", {})
    if not rates:
        await update.message.reply_text("⚠️ الأسعار غير متاحة دلوقتي")
        return

    result = convert(amount, from_cur, to_cur, rates)
    if result is None:
        await update.message.reply_text("❌ كود العملة غلط أو مش موجود")
        return

    rate = result / amount if amount else 0
    text_out = (
        f"💱 `{amount:,.2f} {from_cur}`\n"
        f"⬇️\n"
        f"💰 `{result:,.4f} {to_cur}`\n\n"
        f"📊 1 {from_cur} = `{rate:,.4f}` {to_cur}"
    )
    await update.message.reply_text(text_out, parse_mode="Markdown")


async def rates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسعار عملة ما أمام عملات شائعة"""
    if not context.args:
        await update.message.reply_text(
            "ابعتلي كود العملة، مثلاً:\n`/rates USD`",
            parse_mode="Markdown",
        )
        return

    code = context.args[0].upper()
    rates = load_rates().get("rates", {})
    if code not in rates:
        await update.message.reply_text(f"❌ كود العملة `{code}` مش موجود.")
        return

    # عرض أهم 15 عملة شائعة
    popular = ["USD", "EUR", "GBP", "JPY", "SAR", "AED", "EGP", "KWD",
               "QAR", "CNY", "INR", "TRY", "RUB", "CAD", "AUD"]
    lines = [f"💰 **أسعار {code} ({get_currency_name(code)}):**\n"]
    if code != "USD":
        base_to_usd = 1 / rates[code]
        lines.append(f"1 {code} = `{base_to_usd:.4f}` USD\n")
    else:
        lines.append("")

    for cur in popular:
        if cur == code:
            continue
        if cur == "USD":
            value = 1 / rates[code] if code != "USD" else 1
            lines.append(f"`{value:,.4f}` USD 🇺🇸")
        else:
            value = convert(1, code, cur, rates)
            if value:
                lines.append(f"`{value:,.4f}` {cur} {get_currency_emoji(cur)}")

    last = load_rates()
    if last.get("last_update"):
        lines.append(f"\n🕐 آخر تحديث: `{datetime.fromtimestamp(last['last_update']).strftime('%Y-%m-%d %H:%M')}`")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def popular_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أشهر العملات وأسعارها"""
    rates = load_rates().get("rates", {})
    if not rates:
        await update.message.reply_text("⚠️ الأسعار غير متاحة.")
        return

    popular = ["USD", "EUR", "GBP", "SAR", "AED", "EGP", "KWD", "QAR", "JPY", "CNY"]
    lines = ["📊 **أسعار العملات الشائعة أمام USD:**\n"]
    for cur in popular:
        if cur in rates:
            rate = rates[cur]
            name = get_currency_name(cur)
            lines.append(f"{get_currency_emoji(cur)} **{cur}** ({name}): `1 USD = {rate:,.4f} {cur}`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ====================== إلغاء المحادثة ======================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم الإلغاء", reply_markup=build_main_keyboard())
    return ConversationHandler.END


# ====================== التشغيل الرئيسي ======================
def main():
    if BOT_TOKEN == "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ لازم تحط BOT_TOKEN في متغير البيئة أو تعدّل الكود")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # معالج محادثة التحويل
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("convert", convert_command),
            MessageHandler(filters.Regex(r"^💱 تحويل سريع$"), convert_command),
        ],
        states={
            SELECT_FROM: [
                CallbackQueryHandler(from_currency_selected, pattern=r"^(cur_from_|page_from_)"),
                CallbackQueryHandler(from_currency_selected, pattern=r"^cancel$"),
            ],
            SELECT_TO: [
                CallbackQueryHandler(to_currency_selected, pattern=r"^(cur_to_|page_to_)"),
                CallbackQueryHandler(to_currency_selected, pattern=r"^cancel$"),
            ],
            ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_entered)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rates", rates_command))
    app.add_handler(CommandHandler("popular", popular_currencies))
    app.add_handler(conv_handler)
    # الرسائل العادية (تحويل سريع بالنص)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        quick_convert,
    ))

    # جدولة تحديث الأسعار كل ساعة
    app.job_queue.run_repeating(update_rates_job, interval=UPDATE_INTERVAL, first=10)
    # تحديث فوري عند البدء
    app.job_queue.run_once(update_rates_job, when=5)

    print("✅ البوت شغال...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

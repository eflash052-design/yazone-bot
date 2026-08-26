import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import google.generativeai as genai

# Render ፖርት እንዲያገኝ በቀላል HTTP Server ማዘጋጀት
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID") # የአድሚን Telegram ID
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

# /start ሲባል የሚወጣው የመነሻ መልዕክት እና ቁልፎች
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **እንኳን ወደ Yazone Store አጋዥ ቦት በደህና መጡ!**\n"
        "*(Welcome to Yazone Store Support Bot!)*\n\n"
        "⬇️ **ከታች የሚፈልጉትን ቁልፍ መርጠው ይጫኑ፦**"
    )

    keyboard = [
        [InlineKeyboardButton("🛍️ ምርት ለማዘዝ (Order Product)", callback_data='order')],
        [InlineKeyboardButton("💬 ሀሳብና አስተያየት (Feedback)", callback_data='feedback')],
        [InlineKeyboardButton("📜 ህግና ደንቦች (Rules)", callback_data='rules')],
        [InlineKeyboardButton("ℹ️ ስለ እኛ (About Us)", callback_data='about')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# ቁልፎቹ ሲነኩ የሚወጣው ምላሽ
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    back_button = [[InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ ተመለስ (Main Menu)", callback_data='main_menu')]]

    if query.data == 'main_menu':
        await start(update, context)
        return

    # 1. ምርት ለማዘዝ ሲጫኑ
    elif query.data == 'order':
        text = (
            "📦 **ምርት ለማዘዝ / To Order:**\n\n"
            "1. እባክዎን የሚፈልጉትን የምርት ብራንድ ፎቶ ይላኩልን።\n"
            "2. ለመቼ እንደፈለጉት እለተ ቀኑን አብረው ያስገቡ።\n\n"
            "*(ፎቶውን እና ቀኑን አሁኑኑ እዚህ ቦት ላይ መላክ ይችላሉ!)*"
        )
    
    # 2. ሀሳብና አስተያየት ሲጫኑ
    elif query.data == 'feedback':
        text = (
            "💬 **ሀሳብና አስተያየት / Feedback:**\n\n"
            "ስለ አሰራራችን የእርስዎን መግለጫና አስተያየት ያጋሩን! "
            "ማንኛውንም አስተያየት እዚህ ላይ መጻፍ ይችላሉ።"
        )

    # 3. ህግና ደንቦች ሲጫኑ
    elif query.data == 'rules':
        text = (
            "📜 **የYazone Store ህግና ደንቦች / Rules & Regulations**\n\n"
            "በዚህ የኦንላይን ገበያ የመልእክት ልውውጦች ሰላማዊና አስተማማኝ እንዲሆኑ እባክዎን የሚከተሉትን ህጎች ያንብቡ፦\n\n"
            "1️⃣ **ስለ ሽያጭና ክፍያ (Sales & Payment)**\n"
            "• **የእቃ ጥራት:** የሚቀርቡት የመዋቢያና የኤሌክትሮኒክስ እቃዎች ሙሉ በሙሉ ትክክለኛና የተረጋገጡ ናቸው።\n"
            "• **ትዕዛዝ ማዘዝ:** ማንኛውንም ምርት ለመግዛት ከላይ የተጠቀሱትን አድሚኖች/ቦት ብቻ ያውሩ።\n"
            "• **ክፍያ እና ርክክብ:** ክፍያ ከመፈጸምዎ በፊት የዕቃውን አይነት ከአድሚን ጋር ያረጋግጡ። ከተገለጹት የባንክ አካውንቶች ውጪ ለሚደረግ ክፍያ ኃላፊነት አንወስድም።\n\n"
            "2️⃣ **የኮሙዩኒኬሽን እና የግሩፕ ስነ-ስርዓት (Group Rules)**\n"
            "• **የተከለከሉ ይዘቶች:** አላስፈላጊ ማስታወቂያዎች (Spam)፣ የሌሎች ቻናሎች ሊንክ (Links)፣ ማንኛውንም ሃይማኖታዊ፣ ፖለቲካዊ፣ የብልግና ወይም አክራሪነት ይዘቶችን መላክ በጥብቅ የተከለከለ ነው።\n"
            "• **የተከለከለ ባህሪ:** በአባላት ወይም በአድሚኖች ላይ የሚደረግ ማንኛውም ስድብ ወይም ያልተገባ ንግግር ወዲያውኑ ያስ Ban ያደርጋል።\n"
            "• **ደህንነት:** ማንኛውም ሰው በግል (Inbox) ገብቶ ሊንክ ቢልክልዎ ወይም ገንዘብ ቢጠይቅዎ አይመኑ።\n\n"
            "3️⃣ **የአገልግሎት ሰዓት እና ድጋፍ**\n"
            "• ማንኛውም ጥያቄ ካለዎት ለአድሚን መልእክት ማስቀመጥ ይችላሉ፤ በቅርብ ጊዜ ውስጥ ምላሽ እንሰጣለን።\n"
            "• ቦቱና ግሩፑ በራስ-ሰር (Automated) የሚደራጅ በመሆኑ ህጉን የማይከተሉትን ሲስተሙ በራሱ ያስወጣል።"
        )

    # 4. ስለ እኛ ሲጫኑ
    elif query.data == 'about':
        text = (
            "ℹ️ **ስለ እኛ / About Us - Yazone Store**\n\n"
            "1️⃣ **መግቢያ**\n"
            "**Yazone Store** ጥራት ያላቸውን የውበት (ኮስሞቲክስ) እና የኤሌክትሮኒክስ ምርቶች በተጣጣመ ዋጋ ለደንበኞች የሚያቀርብ የኦንላይን ገበያ ነው።\n"
            "**ዓላማችን:** ደንበኞቻችን ካሉበት ቦታ ሳይንገላቱ የሚፈልጉትን ምርት በታማኝነትና በፍጥነት እንዲያገኙ ማድረግ ነው።\n\n"
            "2️⃣ **ለምን እኛን ይመርጣሉ?**\n"
            "• **ጥራት ያላቸው ምርቶች:** ተስፋ የተሰጣቸውን ምርቶች ብቻ እናቀርባለን።\n"
            "• **ተጣጣመ ዋጋ:** ከገበያ ጋር የተመጣጠነ እና ግልጽ የዋጋ ተመን።\n"
            "• **ፈጣን ርክክብ:** ያዘዙትን ምርት ባሉበት ቦታ እናደርሳለን።\n\n"
            "3️⃣ **እንዴት ማዘዝ ይቻላል?**\n"
            "1. የሚፈልጉትን ምርት ይምረጡ።\n"
            "2. ለአድሚን ወይም በቦቱ በኩል ትዕዛዝዎን ይላኩ።\n"
            "3. ክፍያ ፈጽመው አድራሻዎን ሲልኩልን ምርቱን እናደርሳለን።\n\n"
            "4️⃣ **የግንኙነት አድራሻ**\n"
            "• ቴሌግራም አድሚን: @Yazone_Admin\n"
            "• ቻናላችን: @YazoneStore"
        )
        
        about_keyboard = [
            [InlineKeyboardButton("📞 አድሚን ለማናገር", url="https://t.me/Yazone_Admin")],
            [InlineKeyboardButton("🛍️ ወደ ምርቶች ካታሎግ", callback_data='order')],
            [InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ ተመለስ", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(about_keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return

    reply_markup = InlineKeyboardMarkup(back_button)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ተጠቃሚው ፎቶ ወይም ጽሁፍ ሲልክ ተቀብሎ አስተናግዶ ለቦቱ ባለቤት (Admin) መላክ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_info = f"👤 **ከደንበኛ የተላከ መልዕክት፦**\n• ስም: {user.full_name}\n• Username: @{user.username if user.username else 'የለውም'}\n• ID: `{user.id}`\n\n"

    # ደንበኛው ፎቶ ሲልክ
    if update.message.photo:
        await update.message.reply_text("✅ መረጃውና ፎቶው ደርሶናል! አድሚኖቻችን ተመልክተው በአጭር ጊዜ ውስጥ ያናግሩዎታል።")
        if ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=user_info + "📸 **የምርት ፎቶ ልኳል፦**", parse_mode='Markdown')
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=update.message.caption if update.message.caption else "")

    # ደንበኛው ጽሁፍ ሲልክ
    elif update.message.text:
        user_text = update.message.text
        
        # ለቦቱ ባለቤት መልዕክቱን መላክ
        if ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=user_info + f"💬 **መልዕክት/ትዕዛዝ፦**\n{user_text}", parse_mode='Markdown')

        # በ AI ምላሽ መስጠት
        try:
            if GEMINI_API_KEY:
                response = model.generate_content(user_text)
                await update.message.reply_text(response.text)
            else:
                await update.message.reply_text("✅ መልዕክትዎ ደርሶናል! በአጭር ጊዜ ውስጥ አድሚኖቻችን ይመልሱልዎታል። አመሰግናለሁ!")
        except Exception:
            await update.message.reply_text("✅ መልዕክትዎ ደርሶናል! በአጭር ጊዜ ውስጥ አድሚኖቻችን ይመልሱልዎታል። አመሰግናለሁ!")

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    
    print("Bot is running...")
    app.run_polling()

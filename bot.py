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

# --- 1. RENDER PORT BINDING (HTTP SERVER) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# --- 2. KEYS & CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

# --- 3. KEYBOARDS ---
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("💄 የመዋቢያ ምርቶች | Cosmetics", callback_data="btn_cosmetics")],
        [InlineKeyboardButton("🔌 የኤሌክትሮኒክስ ምርቶች | Electronics", callback_data="btn_electronics")],
        [InlineKeyboardButton("💬 ሀሳብና አስተያየት | Feedback", callback_data="btn_feedback")],
        [InlineKeyboardButton("📜 ህግና ደንቦች | Rules", callback_data="btn_rules")],
        [InlineKeyboardButton("ℹ️ ስለ እኛ | About Us", callback_data="btn_about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ | Main Menu", callback_data="btn_main_menu")]]
    return InlineKeyboardMarkup(keyboard)

# --- 4. HANDLERS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    welcome_text = (
        "👋 **እንኳን ወደ Yazone Store በሰላም መጡ!**\n"
        "(Welcome to Yazone Store!)\n\n"
        "👇 ከታች የሚፈልጉትን መርጠው ይዘዙ፦\n"
        "(Please select an option below:)"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "btn_main_menu":
        context.user_data.clear()
        welcome_text = "👇 ከታች የሚፈልጉትን መርጠው ይዘዙ፦\n(Please select an option below:)"
        await query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

    elif data in ["btn_cosmetics", "btn_electronics"]:
        category_name = "የመዋቢያ (Cosmetics)" if data == "btn_cosmetics" else "የኤሌክትሮኒክስ (Electronics)"
        context.user_data['category'] = category_name
        context.user_data['state'] = 'WAITING_PRODUCT_INFO'
        
        text = (
            f"🛍️ **የ{category_name} ምርት ማዘዣ**\n\n"
            "እባክዎን የሚፈልጉትን ምርት **ፎቶ** ወይም **ስም** ይላኩልን፦\n"
            "(Please send the photo or exact name of the product you want:)"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif data == "btn_feedback":
        context.user_data['state'] = 'WAITING_FEEDBACK'
        text = (
            "💬 **ሀሳብና አስተያየት | Feedback**\n\n"
            "እባክዎን አስተያየትዎን፣ ጥያቄዎን ወይም መልእክትዎን በጽሁፍ ያስገቡልን፦\n"
            "(Please send us your message or feedback:)"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif data == "btn_rules":
        rules_text = (
            "📜 **የ Yazone Store ህግና ደንቦች | Rules & Regulations**\n\n"
            "1. አላስፈላጊ ማስታወቂያና ሊንክ መላክ የተከለከለ ነው።\n"
            "   (Sending spam or unauthorized links is prohibited.)\n\n"
            "2. ስድብና ያልተገቡ ቃላትን መጠቀም አይቻልም።\n"
            "   (Inappropriate language is strictly prohibited.)\n\n"
            "3. ትዕዛዝ ሲያዙ ትክክለኛ መረጃ፣ አድራሻ እና ቀነ ቀጠሮ ያስገቡ።\n"
            "   (Provide accurate details, address, and preferred delivery date.)\n\n"
            "4. **በአንድነት መስራት፣ ሀሳብ መለዋወጥ እና አብሮ ማደግን እንደግፋለን!**"
        )
        await query.message.edit_text(rules_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif data == "btn_about":
        about_text = (
            "ℹ️ **ስለ Yazone Store | About Us**\n\n"
            "እንኳን ወደ **Yazone Store** በሰላም መጡ! እኛ የሚፈልጉትን ጥራት ያላቸው የመዋቢያ እና የኤሌክትሮኒክስ ምርቶች በተጣጣመ ዋጋ እና በታማኝነት እናቀርባለን።"
        )
        await query.message.edit_text(about_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    user = update.effective_user
    text_content = update.message.text or update.message.caption or ""

    # STEP 1: Customer sends product photo or name
    if state == 'WAITING_PRODUCT_INFO':
        context.user_data['product_info'] = text_content if text_content else "የምርት ፎቶ ተልኳል (Product Photo Sent)"
        if update.message.photo:
            context.user_data['photo_id'] = update.message.photo[-1].file_id

        context.user_data['state'] = 'WAITING_DATE_ADDRESS'
        await update.message.reply_text(
            "በጣም ጥሩ! አሁን ደግሞ የሚከተሉትን መረጃዎች በአንድ ላይ ጽፈው ይላኩልን፦\n\n"
            "1. **ስልክ ቁጥርዎ**\n"
            "2. **እቃው እንዲደርስዎት የሚፈልጉበት ቀን (ቀነ-ቀጠሮ)**\n"
            "3. **ትክክለኛ አድራሻዎ**\n\n"
            "(Please send your Phone Number, Preferred Delivery Date, and Address:)",
            reply_markup=get_back_keyboard()
        )

    # STEP 2: Customer sends details -> Send complete order to Admin
    elif state == 'WAITING_DATE_ADDRESS':
        context.user_data['date_address'] = text_content
        category = context.user_data.get('category', 'ምርት')
        product_info = context.user_data.get('product_info', 'የተላከ ፎቶ/መረጃ')
        date_address = context.user_data.get('date_address', '')
        photo_id = context.user_data.get('photo_id')

        admin_msg = (
            "🚨 **አዲስ ትዕዛዝ ደርሷል! (New Order)**\n\n"
            f"🏷️ **ምድብ:** {category}\n"
            f"📦 **የተጠየቀው ምርት/ፎቶ:** {product_info}\n\n"
            f"📋 **የደንበኛ መረጃ (ስልክ/ቀን/አድራሻ):**\n{date_address}\n\n"
            f"👤 **የደንበኛ ስም:** {user.full_name}\n"
            f"💬 **Telegram:** @{user.username if user.username else 'የለውም'}\n"
            f"🆔 **User ID:** `{user.id}`"
        )

        if ADMIN_ID != 0:
            if photo_id:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_msg, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")

        await update.message.reply_text(
            "✅ **ትዕዛዝዎ በጥሩ ሁኔታ ደርሶናል!**\n\n"
            "የመረጡትን ምርት ዋጋ አጣርተን በቅርቡ በስልክ ወይም በቴሌግራም እናሳውቅዎታለን። እናመሰግናለን!\n"
            "(We will check the price and get back to you shortly. Thank you!)",
            reply_markup=get_back_keyboard()
        )
        context.user_data.clear()

    # Feedback Handling
    elif state == 'WAITING_FEEDBACK':
        fb_msg = (
            "💬 **አዲስ አስተያየት ደርሷል!**\n\n"
            f"📝 **መልእክት:** {text_content}\n\n"
            f"👤 **ስም:** {user.full_name}\n"
            f"💬 **Telegram:** @{user.username if user.username else 'የለውም'}\n"
            f"🆔 **User ID:** `{user.id}`"
        )
        if ADMIN_ID != 0:
            await context.bot.send_message(chat_id=ADMIN_ID, text=fb_msg, parse_mode="Markdown")

        await update.message.reply_text(
            "✅ ሀሳብና አስተያየትዎ ደርሶናል! ስለሰጡን አስተያየት እናመሰግናለን።",
            reply_markup=get_back_keyboard()
        )
        context.user_data.clear()

    # AI Chat via Gemini for general questions
    else:
        if model:
            try:
                response = model.generate_content(text_content)
                await update.message.reply_text(response.text)
            except Exception:
                await update.message.reply_text(
                    "እባክዎን ከታች ካሉት አማራጮች ይጠቀሙ፦",
                    reply_markup=get_main_keyboard()
                )
        else:
            await update.message.reply_text(
                "እባክዎን ከታች ካሉት አማራጮች አንዱን ይምረጡ፦",
                reply_markup=get_main_keyboard()
            )

# --- 5. MAIN EXECUTION ---
def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_click_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import re
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Secrets Configuration
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID', '123456789')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Configure Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

FULL_NAME, PHONE, ADDRESS_MEDIA = range(3)

# 1. /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💄 መዋቢያዎች (Cosmetics)", callback_data='cat_cosmetics')],
        [InlineKeyboardButton("📱 ኤሌክትሮኒክስ (Electronics)", callback_data='cat_electronics')],
        [InlineKeyboardButton("📜 ህግና ደንቦች (Rules)", callback_data='show_rules')],
        [InlineKeyboardButton("📞 እኛን ለማነጋገር", callback_data='contact_us')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "እንኳን ወደ Yazone Store እና የማህበረሰብ ቦት በደህና መጡ! 👋\n\n"
        "• ምርቶችን ለመግዛት ከታች ባሉት ቁልፎች ይመረጡ።\n"
        "• ማንኛውንም ጥያቄ በፈለጉት ቋንቋ ቢጽፉልኝ በ AI አስልቼ እመልስልዎታለሁ!"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

# 2. Button Handlers
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'cat_cosmetics':
        keyboard = [
            [InlineKeyboardButton("✨ የፊት ክሬም - 1,500 ብር", callback_data='item_face_cream')],
            [InlineKeyboardButton("💄 ሊፕስቲክ Set - 800 ብር", callback_data='item_lipstick')],
            [InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ", callback_data='back_to_main')]
        ]
        await query.edit_message_text("💅 **የመዋቢያ ምርቶች ካታሎግ**\nየሚፈልጉትን እቃ ይምረጡ፦", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'cat_electronics':
        keyboard = [
            [InlineKeyboardButton("🎧 ኤርፎን (Airpods) - 2,500 ብር", callback_data='item_airpods')],
            [InlineKeyboardButton("⌚ ስማርት ዋች (Smart Watch) - 3,200 ብር", callback_data='item_watch')],
            [InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ", callback_data='back_to_main')]
        ]
        await query.edit_message_text("🔌 **የኤሌክትሮኒክስ ምርቶች ካታሎግ**\nየሚፈልጉትን እቃ ይምረጡ፦", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('item_'):
        item_names = {
            'item_face_cream': 'የፊት ክሬም (Face Cream) - 1,500 ብር',
            'item_lipstick': 'ሊፕስቲክ (Lipstick Set) - 800 ብር',
            'item_airpods': 'ብሉቱዝ ኤርፎን (Airpods) - 2,500 ብር',
            'item_watch': 'ስማርት ዋች (Smart Watch) - 3,200 ብር'
        }
        selected_item = item_names.get(query.data, 'ያልታወቀ እቃ')
        context.user_data['selected_item'] = selected_item

        keyboard = [
            [InlineKeyboardButton("🛒 አሁን እዝዝ (Order Now)", callback_data='start_order')],
            [InlineKeyboardButton("🔙 ወደ ካቴጎሪ ተመለስ", callback_data='back_to_main')]
        ]
        await query.edit_message_text(
            f"📦 **የመረጡት ምርት:**\n{selected_item}\n\nይህን እቃ ማዘዝ ይፈልጋሉ?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'show_rules':
        rules_text = (
            "📜 **የ Yazone Store እና የግሩፕ ህግና ደንቦች፦**\n\n"
            "1. አላስፈላጊ ማስታወቂያና ሊንክ መላክ በጥብቅ የተከለከለ ነው (ቦቱ ወዲያው ያጠፋዋል)።\n"
            "2. በማህበረሰቡ ውስጥ ስድብና ያልተገቡ ቃላትን መጠቀም አይቻልም።\n"
            "3. ትዕዛዝ ሲያዙ ትክክለኛ ስምና ስልክ ቁጥር ማስገባት አለብዎት።\n"
            "4. ለየትኛውም ጥያቄ ቦቱን በፈለጉት ቋንቋ መጠየቅ ይችላሉ።"
        )
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ", callback_data='back_to_main')]]
        await query.edit_message_text(rules_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'contact_us':
        keyboard = [[InlineKeyboardButton("🔙 ወደ ዋናው ማውጫ", callback_data='back_to_main')]]
        await query.edit_message_text("📞 **እኛን ለማነጋገር:**\n📱 ስልክ: 0911XXXXXX\n💬 ቴሌግራም: @YourUsername", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'back_to_main':
        await start(update, context)

# 3. Order Conversation Flow
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🛒 **በትዕዛዝ ሂደት ላይ ነዎት**\n\nእባክዎን **ሙሉ ስምዎን** ያስገቡ፦")
    return FULL_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text("እናመሰግናለን! አሁን **የስልክ ቁጥርዎን** ያስገቡ፦")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "📍 **አድራሻ እና ተጨማሪ መረጃ፦**\n\n"
        "የሚደርሱበትን አድራሻ በጽሁፍ፣ በፎቶ፣ በቪዲዮ፣ በድምፅ (Voice) ወይም Location ይላኩ፦"
    )
    return ADDRESS_MEDIA

async def get_address_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = context.user_data.get('selected_item', 'ያልተጠቀሰ ምርት')
    name = context.user_data.get('full_name')
    phone = context.user_data.get('phone')
    user_info = update.effective_user

    await update.message.reply_text(
        "✅ **ትዕዛዝዎ በተሳካ ሁኔታ ተልኳል!**\n\n"
        "የላኩትን መረጃ ተቀብለናል፤ በቅርቡ ደውለን እናረጋግጣለን። እናመሰግናለን!"
    )

    summary_text = (
        f"🚨 **አዲስ ትዕዛዝ ደርሷል!**\n\n"
        f"🛍 **የታዘዘው እቃ:** {item}\n"
        f"👤 **ስም:** {name}\n"
        f"📞 **ስልክ:** {phone}\n"
        f"💬 **Telegram:** @{user_info.username or 'የለውም'}\n"
        f"🆔 **User ID:** `{user_info.id}`"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=summary_text, parse_mode="Markdown")

    if update.message.text:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📍 **አድራሻ (ጽሁፍ):**\n{update.message.text}")
    elif update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption="📸 **የተላከ ፎቶ**")
    elif update.message.voice:
        await context.bot.send_voice(chat_id=ADMIN_ID, voice=update.message.voice.file_id, caption="🎙 **የተላከ ድምፅ (Voice)**")
    elif update.message.video:
        await context.bot.send_video(chat_id=ADMIN_ID, video=update.message.video.file_id, caption="🎥 **የተላከ ቪዲዮ**")
    elif update.message.location:
        loc = update.message.location
        await context.bot.send_location(chat_id=ADMIN_ID, latitude=loc.latitude, longitude=loc.longitude)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ትዕዛዙ ተሰርዟል።")
    return ConversationHandler.END

# 4. Group Moderation (Anti-Link Protection)
async def group_moderator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    # Check if message contains URLs or Telegram links
    url_pattern = r'(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+)'
    if re.search(url_pattern, message.text):
        try:
            await message.delete()
            warning = await message.chat.send_message(
                f"⚠️ @{message.from_user.username or message.from_user.first_name}፣ በግሩፑ ውስጥ አላስፈላጊ ሊንክ ወይም ማስታወቂያ መላክ የተከለከለ ነው!"
            )
        except Exception as e:
            print(f"Error in moderation: {e}")

# 5. AI Chat Handler (Multi-language Support using Gemini)
async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not model:
        await update.message.reply_text("ይቅርታ፣ AI አገልግሎቱ አሁን አልተዘጋጀም።")
        return

    system_prompt = (
        "You are an intelligent, polite customer service and assistant bot for 'Yazone Store'. "
        "Answer the user's question accurately in whatever language they write in (Amharic, English, etc.). "
        "If they ask about business policies or products, respond professionally and warmly."
    )
    try:
        response = model.generate_content(f"{system_prompt}\n\nUser Question: {user_text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ይቅርታ፣ መልስ ለመስጠት ስሞክር ትንሽ ስህተት አጋጥሞኛል።")

def main():
    app = Application.builder().token(TOKEN).build()

    # Conversation handler for ordering
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order, pattern='^start_order$')],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS_MEDIA: [
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VOICE | filters.VIDEO | filters.LOCATION) & ~filters.COMMAND, 
                    get_address_media
                )
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(button_handler))

    # Anti-link filter for Groups
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, group_moderator))

    # AI Chat filter for Private Chat
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, ai_chat_handler))

    print("Yazone All-in-One Bot መስራት ጀምሯል...")
    app.run_polling()

if __name__ == '__main__':
    main()

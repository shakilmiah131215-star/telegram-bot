import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# লগিং কনফিগারেশন
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# বটের বর্তমান স্ট্যাটাস ও মোড ট্র্যাক করার ভেরিয়েবল
bot_status = {"active": False, "mode": "busy"}

# /start কমান্ডে একটি ইন্টারঅ্যাকティブ প্যানেল পাঠানো
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔴 বট চালু করুন", callback_data="activate")],
        [InlineKeyboardButton("🟢 ব্যাস্ত মোড (Busy)", callback_data="mode_busy")],
        [InlineKeyboardButton("🔵 ঘুম মোড (Sleep)", callback_data="mode_sleep")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    status_text = "বন্ধ আছে ❌"
    if bot_status["active"]:
        current_mode = "ব্যস্তকালীন সময় 🔴" if bot_status["mode"] == "busy" else "ঘুমের সময় 🔵"
        status_text = f"চালু আছে ✅ ({current_mode})"

    await update.message.reply_text(
        f"🤖 **অটো-রিপ্লাই কন্ট্রোল প্যানেল**\nবর্তমান অবস্থা: {status_text}\n\nনিচের বোতামগুলো থেকে যেকোনো একটি অপشن নির্বাচন করুন:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# বটন ক্লিক করলে কাজ পরিচালনা করার হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "activate":
        bot_status["active"] = False
        await query.edit_message_text(text="❌ বটটি-ডিঅ্যাক্টিভ (Deactivated) করা হয়েছে!")

    elif query.data == "mode_busy":
        bot_status["active"] = True
        bot_status["mode"] = "busy"
        await query.edit_message_text(text="✅ অ্যাক্টিভ করা হয়েছে!\n\nবটের মোড: **'ব্যস্তকালীন সময়ে তে আছি'** পরে কথা বলব।", parse_mode="Markdown")

    elif query.data == "mode_sleep":
        bot_status["active"] = True
        bot_status["mode"] = "sleep"
        await query.edit_message_text(text="✅ অ্যাক্টিভ করা হয়েছে!\n\nবটের মোড: **'আমি এখন ঘুমচ্ছি ঘুম থেকে উঠে আপনার সাথে যোগাযোগ করব'**।", parse_mode="Markdown")

# কেউ মেসেজ দিলে অটো-রিপ্লাই পাঠানোর হ্যান্ডলার
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if bot_status["active"] and update.message and update.message.chat.type == "private":
        if bot_status["mode"] == "busy":
            reply_text = "আমি এখন ব্যস্ত আছি পরে কথা বলব।"
        else:
            reply_text = "আমি এখন ঘুমচ্ছি ঘুম থেকে উঠে আপনার সাথে যোগাযোগ করব।"
        
        await update.message.reply_text(reply_text)

def main():
    # আপনার টেলিগ্রাম বট টোকেন
    TOKEN = "9271289264:AAEIJCiBo4L4xzBWFNTj1VtAA2sA0r8L3BM"

    application = ApplicationBuilder().token(TOKEN).build()

    # হ্যান্ডলারগুলো রেজিস্টার করা
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_reply))

    print("Bot is running...")
    
    # Render-এর ইভেন্ট লুপের সমস্যা সমাধানের জন্য সঠিক উপায়ে রানিং
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    main()

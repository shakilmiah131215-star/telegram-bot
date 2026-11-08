import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# লগিং সেটআপ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# বটের বর্তমান স্টেট ও মোড ট্র্যাক করার জন্য
bot_status = {"active": False, "mode": "busy"}  # ডিফল্টভাবে অফ থাকবে

# ১. /start কমান্ড এবং কন্ট্রোল প্যানেল দেখানোর জন্য
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔴 বট বন্ধ রাখুন", callback_data="deactivate")],
        [InlineKeyboardButton("🟢 মোড ১: মোবাইল হাতে নেই", callback_data="mode_busy"),
         InlineKeyboardButton("🟢 মোড ২: ঘুমাচ্ছি", callback_data="mode_sleep")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status_text = "বন্ধ আছে ❌"
    if bot_status["active"]:
        current_mode = "মোবাইল হাতে নেই 📵" if bot_status["mode"] == "busy" else "ঘুমাচ্ছি 😴"
        status_text = f"চালু আছে ✅ ({current_mode})"
        
    await update.message.reply_text(
        f"🤖 **অটো-রিপ্লাই কন্ট্রোল প্যানেল**\n\nবর্তমান অবস্থা: {status_text}\n\nনিচের বাটনগুলো থেকে যেকোনো একটি মোড সিলেক্ট করুন:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ২. বাটনে ক্লিক করলে মোড পরিবর্তন করার হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "deactivate":
        bot_status["active"] = False
        await query.edit_message_text(text="❌ অটো-রিপ্লাই নিষ্ক্রিয় (Deactivated) করা হয়েছে।")
        
    elif query.data == "mode_busy":
        bot_status["active"] = True
        bot_status["mode"] = "busy"
        await query.edit_message_text(text="✅ অ্যাক্টিভ করা হয়েছে!\n\nরিপ্লাই যাবে: *মোবাইলটি আমার হাতে নেই পরে কথা হবে।*", parse_mode="Markdown")
        
    elif query.data == "mode_sleep":
        bot_status["active"] = True
        bot_status["mode"] = "sleep"
        await query.edit_message_text(text="✅ অ্যাক্টিভ করা হয়েছে!\n\nরিপ্লাই যাবে: *আমি এখন ঘুমোচ্ছি ঘুম থেকে উঠে আপনার সাথে আগে কথা বলবো।*", parse_mode="Markdown")

# ৩. কেউ মেসেজ দিলে অটো-রিপ্লাই পাঠানোর হ্যান্ডলার
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if bot_status["active"] and update.message and update.message.chat.type == "private":
        if bot_status["mode"] == "busy":
            reply_text = "মোবাইলটি আমার হাতে নেই পরে কথা হবে।"
        else:
            reply_text = "আমি এখন ঘুমোচ্ছি ঘুম থেকে উঠে আপনার সাথে আগে কথা বলবো।"
            
        await update.message.reply_text(reply_text)

def main():
    # আপনার টোকেনটি এখানে বসানো হয়েছে
    TOKEN = "9271289264:AAEIJCiBo4L4xzBWFNTj1VtAA2sA0r8L3BM"
    
    application = ApplicationBuilder().token(TOKEN).build()

    # হ্যান্ডলার রেজিস্টার করা
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_reply))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
import logging
import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# লগিং কনফিগারেশন
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔑 আপনার নির্দিষ্ট সিক্রেট মাস্টার পাসওয়ার্ড
SECRET_TRIGGER = "#admin_unlock_99"

# 👤 আপনার ফেক প্রোফাইলের তথ্য
PROFILE_NAME = "Ripon Miah"
PROFILE_USERNAME = "SleepAutoReplyBot"
PROFILE_PHOTO_URL = "https://i.imgur.com/YourProfilePic.jpg"

# অ্যাডমিন ও লিড স্টোরেজ
active_admins = set()
inbox_leads = {}

GROUP_LINKS = [
    ("🦋 BOOST THE LION 🦁", "https://t.me/your_group_1"),
    ("A.S.M.R WORKING", "https://t.me/your_group_2"),
    ("Facebook Update Method", "https://t.me/your_group_3")
]

# --- ছোট ফ্লাস্ক সার্ভার (রেন্ডারের Web Service "Timed Out" সমস্যা সমাধানের জন্য) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Stealth Bot is Active & Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# টেলিগ্রাম ইনকামিং মেসেজ হ্যান্ডলার
async def handle_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    user = update.message.from_user
    chat_type = update.message.chat.type
    text = update.message.text.strip() if update.message.text else ""

    if chat_type != "private":
        return

    # ১. সঠিক সিক্রেট কোড দিলে অ্যাডমিন প্যানেল ও বাটনগুলো শো করবে
    if text == SECRET_TRIGGER:
        active_admins.add(user.id)
        
        keyboard = [
            [InlineKeyboardButton("📊 ইনবক্স লিড ও নোট বক্স", callback_data="show_leads")],
            [InlineKeyboardButton("🔗 গ্রুপ লিংক ম্যানেজমেন্ট", callback_data="show_groups")],
            [InlineKeyboardButton("🔒 অ্যাডমিন মোড বন্ধ করুন (Lock)", callback_data="admin_logout")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔓 **পাসওয়ার্ড সঠিক! সিক্রেট কন্ট্রোল প্যানেল আনলক করা হয়েছে।**\n\n"
            f"📥 মোট সংগৃহীত লিড: `{len(inbox_leads)} জন`\n"
            f"নিচের অপশনগুলো ব্যবহার করুন:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # যদি ইউজার ইতিমধ্যে অ্যাডমিন মোডে থাকে
    if user.id in active_admins:
        return

    # ২. সাধারণ ভিজিটর মেসেজ দিলে নোট করা ও ফেক প্রোফাইল দেখানো
    inbox_leads[user.id] = {
        "name": user.full_name,
        "username": f"@{user.username}" if user.username else "ইউজারনেম নেই",
        "last_msg": text if text else "মিডিয়া/ফাইল"
    }

    profile_keyboard = [
        [InlineKeyboardButton("💬 Message", url=f"https://t.me/{PROFILE_USERNAME}")],
        [InlineKeyboardButton("🔔 Mute", callback_data="fake_action"), InlineKeyboardButton("📞 Call", callback_data="fake_action")],
        [InlineKeyboardButton("📁 Channel & Groups", callback_data="visitor_groups")]
    ]
    
    profile_caption = (
        f"👤 **{PROFILE_NAME}**\n"
        f"_last seen recently_\n\n"
        f"📢 **Channel:** FACABOOK OLD ID SELL\n"
        f"📌 Pc clone id sell\n\n"
        f"🔗 **Username:** `@{PROFILE_USERNAME}`\n\n"
        f"👇 আমাদের গ্রুপগুলোতে যুক্ত হতে নিচে ক্লিক করুন:"
    )

    try:
        await update.message.reply_photo(
            photo=PROFILE_PHOTO_URL,
            caption=profile_caption,
            reply_markup=InlineKeyboardMarkup(profile_keyboard),
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(
            profile_caption,
            reply_markup=InlineKeyboardMarkup(profile_keyboard),
            parse_mode="Markdown"
        )

# বাটন হ্যান্ডলার (ক্লিক করলে কী কাজ করবে)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "visitor_groups":
        group_keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in GROUP_LINKS]
        group_keyboard.append([InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_profile")])
        await query.edit_message_caption(
            caption="📁 **আমাদের যুক্ত থাকা গ্রুপগুলোর তালিকা:**\nনিচের লিংকে ক্লিক করে জয়েন করুন:",
            reply_markup=InlineKeyboardMarkup(group_keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "back_profile":
        profile_keyboard = [
            [InlineKeyboardButton("💬 Message", url=f"https://t.me/{PROFILE_USERNAME}")],
            [InlineKeyboardButton("🔔 Mute", callback_data="fake_action"), InlineKeyboardButton("📞 Call", callback_data="fake_action")],
            [InlineKeyboardButton("📁 Channel & Groups", callback_data="visitor_groups")]
        ]
        await query.edit_message_caption(
            caption=f"👤 **{PROFILE_NAME}**\n_last seen recently_\n\n🔗 **Username:** `@{PROFILE_USERNAME}`",
            reply_markup=InlineKeyboardMarkup(profile_keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "fake_action":
        await query.answer("এটি একটি পার্সোনাল প্রোফাইল ভিউ!", show_alert=False)

    elif user_id in active_admins:
        if query.data == "show_leads":
            if not inbox_leads:
                await query.edit_message_text(text="📥 এখনো কোনো নতুন লিড বা নোট জমা হয়নি।")
                return

            list_text = "📊 **আজকের সংগৃহীত লিড ও নোট বক্স:**\n\n"
            for idx, (uid, data) in enumerate(inbox_leads.items(), 1):
                list_text += f"{idx}. **{data['name']}** ({data['username']})\n   💬 মেসেজ: _{data['last_msg']}_\n\n"

            await query.edit_message_text(text=list_text, parse_mode="Markdown")

        elif query.data == "show_groups":
            group_keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in GROUP_LINKS]
            await query.edit_message_text(text="আপনার সেট করা গ্রুপ লিংকগুলো:", reply_markup=InlineKeyboardMarkup(group_keyboard))

        elif query.data == "admin_logout":
            active_admins.remove(user_id)
            await query.edit_message_text(text="🔒 এই অ্যাকাউন্টের জন্য অ্যাডমিন মোড লক করা হয়েছে। আবার প্যানেল খুলতে সিক্রেট কোড দিন।")

def main():
    TOKEN = "9271289264:AAEIJCiBo4L4xzBWFNTj1VtAA2sA0r8L3BM"
    
    # ব্যাকগ্রাউন্ডে ফ্লাস্ক সার্ভার চালু রাখা
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_incoming))

    print("Stealth Bot with Flask Web Server is running...")
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    main()

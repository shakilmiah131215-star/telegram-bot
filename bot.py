import json
import logging
import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# লগিং কনফিগারেশন
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔑 সিক্রেট মাস্টার পাসওয়ার্ড
SECRET_TRIGGER = "#admin_unlock_99"

# 👤 প্রোফাইলের তথ্য
PROFILE_NAME = "Ripon Khan"
PROFILE_USERNAME = "millions_b"
PROFILE_PHOTO_URL = "https://i.imgur.com/YourProfilePic.jpg"

# অ্যাডমিন ও পার্মানেন্ট ফাইল স্টোরেজ
active_admins = set()
LEAD_FILE = "leads.json"

def load_leads():
    if os.path.exists(LEAD_FILE):
        try:
            with open(LEAD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_leads(leads):
    try:
        with open(LEAD_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving leads: {e}")

# আপনার দেওয়া নতুন ও সমস্ত সুনির্দিষ্ট কিওয়ার্ড লিস্ট
TARGET_KEYWORDS = [
    "pc clone id need", 
    "pc, ", 
    "61x", 
    "1000x", 
    "1000xx", 
    "1000X", 
    "need"
]

GROUP_LINKS = [
    ("🦋 BOOST THE LION 🦁", "https://t.me/your_group_1"),
    ("A.S.M.R WORKING", "https://t.me/your_group_2"),
    ("Facebook Update Method", "https://t.me/your_group_3")
]

# রেন্ডার সার্ভার টিক রাখার জন্য ফ্লাস্ক
app = Flask(__name__)

@app.route('/')
def home():
    return "Advanced Keyword CRM Bot is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# মেসেজ হ্যান্ডলার (ইনবক্স ও গ্রুপ ট্র্যাকিং)
async def handle_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    user = update.message.from_user
    chat_type = update.message.chat.type
    text = update.message.text.strip() if update.message.text else ""
    text_lower = text.lower()

    inbox_leads = load_leads()

    # --- ১. গ্রুপে স্মার্ট কিওয়ার্ড ট্র্যাকিং ---
    if chat_type in ["group", "supergroup"]:
        matched_keyword = "সাধারণ কিওয়ার্ড"
        is_matched = False

        for kw in TARGET_KEYWORDS:
            if kw.lower() in text_lower:
                is_matched = True
                matched_keyword = kw.upper()
                break

        if is_matched:
            inbox_leads[str(user.id)] = {
                "name": user.full_name,
                "username": f"@{user.username}" if user.username else "ইউজারনেম নেই",
                "last_msg": text,
                "keyword": matched_keyword,
                "source": f"Group ({update.message.chat.title})"
            }
            save_leads(inbox_leads)
        return

    # --- ২. ইনবক্সে কাজ (Private Chat) ---
    if chat_type == "private":
        if text == SECRET_TRIGGER:
            active_admins.add(user.id)
            
            keyboard = [
                [InlineKeyboardButton("📊 সংগৃহীত লিড ও নোট বক্স", callback_data="show_leads")],
                [InlineKeyboardButton("🔗 গ্রুপ লিংক লিস্ট ও জয়েন অপশন", callback_data="show_groups")],
                [InlineKeyboardButton("🔒 অ্যাডমিন মোড বন্ধ করুন", callback_data="admin_logout")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🔓 **অ্যাডমিন প্যানেল আনলক সফল!**\n\n"
                f"📥 মোট সংগৃহীত লিড: `{len(inbox_leads)} জন`\n"
                f"নিচের অপশন থেকে পরিচালনা করুন:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return

        if user.id in active_admins:
            return

        # ইনবক্সে মেসেজ দিলে ট্যাগসহ সেভ করা
        inbox_leads[str(user.id)] = {
            "name": user.full_name,
            "username": f"@{user.username}" if user.username else "ইউজারনেম নেই",
            "last_msg": text if text else "মিডিয়া/ফাইল",
            "keyword": "Direct Inbox",
            "source": "Direct Inbox"
        }
        save_leads(inbox_leads)

        # ফেক প্রোফাইল ভিউ
        profile_keyboard = [
            [InlineKeyboardButton("💬 Message (Direct Chat)", url=f"https://t.me/{PROFILE_USERNAME}")],
            [InlineKeyboardButton("🔔 Mute", callback_data="fake_action"), InlineKeyboardButton("📞 Call", callback_data="fake_action")],
            [InlineKeyboardButton("📁 Groups & Search", callback_data="visitor_groups")]
        ]
        
        profile_caption = (
            f"👤 **{PROFILE_NAME}**\n"
            f"_last seen recently_\n\n"
            f"💻 **PC Clone ID Need & Working Services**\n"
            f"📌 কাজের জন্য ইনবক্সে মেসেজ দিন।\n\n"
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

# বাটন হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    inbox_leads = load_leads()

    if query.data == "visitor_groups":
        group_keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in GROUP_LINKS]
        group_keyboard.append([InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_profile")])
        await query.edit_message_caption(
            caption="📁 **আমাদের উপলব্ধ গ্রুপগুলোর তালিকা:**\nপছন্দের গ্রুপে ক্লিক করে সরাসরি জয়েন হয়ে যান:",
            reply_markup=InlineKeyboardMarkup(group_keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "back_profile":
        profile_keyboard = [
            [InlineKeyboardButton("💬 Message (Direct Chat)", url=f"https://t.me/{PROFILE_USERNAME}")],
            [InlineKeyboardButton("🔔 Mute", callback_data="fake_action"), InlineKeyboardButton("📞 Call", callback_data="fake_action")],
            [InlineKeyboardButton("📁 Groups & Search", callback_data="visitor_groups")]
        ]
        await query.edit_message_caption(
            caption=f"👤 **{PROFILE_NAME}**\n_last seen recently_\n\n💻 **PC Clone ID Need & Services**\n🔗 **Username:** `@{PROFILE_USERNAME}`",
            reply_markup=InlineKeyboardMarkup(profile_keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "fake_action":
        await query.answer("এটি একটি পার্সোনাল প্রোফাইল ভিউ!", show_alert=False)

    elif user_id in active_admins:
        if query.data == "show_leads":
            if not inbox_leads:
                empty_box_text = (
                    "📊 **ইনবক্স ও গ্রুপ লিড নোট বক্স:**\n\n"
                    "📭 **ফাঁকা ঘর:** বর্তমানে কোনো নতুন লিড বা কাস্টমার জমা হয়নি।\n"
                    "_গ্রুপ বা ইনবক্সে কিওয়ার্ড বা 'need' যুক্ত মেসেজ আসলে এখানে দেখাবে।_"
                )
                await query.edit_message_text(text=empty_box_text, parse_mode="Markdown")
                return

            list_text = f"📊 **সংগৃহীত লিড তালিকা (মোট: {len(inbox_leads)} জন):**\n\n"
            for idx, (uid, data) in enumerate(inbox_leads.items(), 1):
                clean_username = data['username'].replace('@', '')
                chat_link = f"t.me/{clean_username}" if data['username'] != "ইউজারনেম নেই" else "ইউজারনেম নেই"
                kw_tag = data.get('keyword', 'General')
                
                list_text += (
                    f"{idx}. **{data['name']}** ({data['username']})\n"
                    f"   🏷️ কিওয়ার্ড ট্যাগ: `{kw_tag}`\n"
                    f"   💬 মেসেজ: _{data['last_msg']}_\n"
                    f"   📍 উৎস: `{data['source']}`\n"
                    f"   🔗 চ্যাট লিংক: {chat_link}\n\n"
                )

            await query.edit_message_text(text=list_text, parse_mode="Markdown")

        elif query.data == "show_groups":
            group_keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in GROUP_LINKS]
            await query.edit_message_text(text="আপনার সেট করা গ্রুপগুলোর তালিকা (ক্লিক করে জয়েন করা যাবে):", reply_markup=InlineKeyboardMarkup(group_keyboard))

        elif query.data == "admin_logout":
            active_admins.remove(user_id)
            await query.edit_message_text(text="🔒 অ্যাডমিন মোড লক করা হয়েছে।")

def main():
    TOKEN = "9271289264:AAEIJCiBo4L4xzBWFNTj1VtAA2sA0r8L3BM"
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_incoming))

    print("Keyword Tagged CRM Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    main()

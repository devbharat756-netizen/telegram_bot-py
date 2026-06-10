import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import db
from razorpay_handler import create_order, verify_payment
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Agar koi file_id ke saath aaya (file access ke liye)
    if context.args:
        file_id = context.args[0]
        await handle_file_access(update, context, file_id)
        return

    keyboard = [
        [InlineKeyboardButton("📦 Plans Dekho & Kharido", callback_data="show_plans")],
        [InlineKeyboardButton("📁 Meri Files", callback_data="my_files")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/YOUR_SUPPORT_USERNAME")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Namaste {user.first_name}!\n\n"
        f"🔐 *Premium Content Access Bot*\n\n"
        f"Yahan aap premium files & documents access kar sakte hain.\n"
        f"Plan kharido aur apni files unlock karo! 🚀",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ========== File Access Handler ==========
async def handle_file_access(update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str):
    user_id = update.effective_user.id
    access = db.get_user_access(user_id)
    
    if access and access['expires_at'] > datetime.now():
        # Access hai — file bot ka link bhejo
        time_left = access['expires_at'] - datetime.now()
        hours_left = int(time_left.total_seconds() // 3600)
        
        file_link = f"https://t.me/{config.FILE_BOT_USERNAME}?start=file_{file_id}"
        keyboard = [[InlineKeyboardButton("📂 File Kholne Ke Liye Yahan Click Karo", url=file_link)]]
        
        await update.message.reply_text(
            f"✅ *Access Confirmed!*\n\n"
            f"⏳ Baaki time: *{hours_left} ghante*\n\n"
            f"Neeche button dabao file dekhne ke liye 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        # Access nahi — plans dikhao
        keyboard = [[InlineKeyboardButton("💳 Plan Kharido", callback_data="show_plans")]]
        await update.message.reply_text(
            f"🔒 *Ye file premium hai!*\n\n"
            f"Is file ko access karne ke liye pehle ek plan kharido.\n"
            f"Hamare plans bahut affordable hain! 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ========== Plans ==========
async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("⚡ 1 Din — ₹50", callback_data="buy_1day")],
        [InlineKeyboardButton("🔥 10 Din — ₹299", callback_data="buy_10day")],
        [InlineKeyboardButton("👑 1 Mahina — ₹399", callback_data="buy_1month")],
        [InlineKeyboardButton("🏠 Back", callback_data="back_home")]
    ]
    
    await query.edit_message_text(
        "💎 *Premium Plans*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *1 Din Access* — ₹50\n"
        "   → Saari files 24 ghante ke liye\n\n"
        "🔥 *10 Din Access* — ₹299\n"
        "   → Saari files 10 din ke liye\n"
        "   → ₹30/din ke hisaab se!\n\n"
        "👑 *1 Mahina Access* — ₹399\n"
        "   → Saari files poore mahine\n"
        "   → Sabse Best Deal! 🎯\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Kaunsa plan lena hai? 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ========== Buy Plan ==========
async def buy_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plan_data = {
        "buy_1day":   {"name": "1 Din", "amount": 50,  "days": 1,  "emoji": "⚡"},
        "buy_10day":  {"name": "10 Din", "amount": 299, "days": 10, "emoji": "🔥"},
        "buy_1month": {"name": "1 Mahina", "amount": 399, "days": 30, "emoji": "👑"},
    }
    
    plan = plan_data.get(query.data)
    if not plan:
        return
    
    user_id = update.effective_user.id
    
    # Razorpay order create karo
    order = create_order(plan['amount'], user_id, plan['days'])
    
    if not order:
        await query.edit_message_text("❌ Payment gateway me problem hai. Thodi der baad try karo.")
        return
    
    # Order DB me save karo
    db.save_order(user_id, order['id'], plan['amount'], plan['days'])
    
    payment_url = f"https://rzp.io/l/{order.get('short_url', '')}"
    
    keyboard = [
        [InlineKeyboardButton(f"💳 ₹{plan['amount']} Pay Karo", url=(payment_url if payment_url and payment_url != "https://rzp.io/l/" else config.RAZORPAY_PAYMENT_LINK))],
        [InlineKeyboardButton("✅ Maine Pay Kar Diya", callback_data=f"verify_{order['id']}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="show_plans")]
    ]
    
    await query.edit_message_text(
        f"{plan['emoji']} *{plan['name']} Plan*\n\n"
        f"💰 Amount: *₹{plan['amount']}*\n"
        f"📅 Access: *{plan['days']} din*\n\n"
        f"*Payment karne ke steps:*\n"
        f"1️⃣ Neeche 'Pay Karo' button dabao\n"
        f"2️⃣ UPI / Card se payment karo\n"
        f"3️⃣ Wapas aao aur 'Maine Pay Kar Diya' dabao\n\n"
        f"🔒 100% Safe & Secure Payment",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ========== Payment Verify ==========
async def verify_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ Payment check ho rahi hai...")
    
    order_id = query.data.replace("verify_", "")
    user_id = update.effective_user.id
    
    order = db.get_order(order_id)
    if not order:
        await query.edit_message_text("❌ Order nahi mila. /start se dobara try karo.")
        return
    
    # Razorpay se verify karo
    is_paid = verify_payment(order_id)
    
    if is_paid:
        # Access do
        days = order['days']
        current = db.get_user_access(user_id)
        if current and current['expires_at'] > datetime.now():
            expires_at = current['expires_at'] + timedelta(days=days)
        else:
            expires_at = datetime.now() + timedelta(days=days)
        db.mark_order_paid(order_id)
        db.grant_access(user_id, expires_at, order_id)
        
        keyboard = [[InlineKeyboardButton("📁 Apni Files Dekho", callback_data="my_files")]]
        
        await query.edit_message_text(
            f"🎉 *Payment Successful!*\n\n"
            f"✅ Aapka access activate ho gaya!\n"
            f"📅 Expire hoga: *{expires_at.strftime('%d %b %Y, %I:%M %p')}*\n\n"
            f"Ab aap saari premium files dekh sakte ho! 🚀",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🔄 Dobara Check Karo", callback_data=f"verify_{order_id}")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/YOUR_SUPPORT_USERNAME")]
        ]
        await query.edit_message_text(
            "⏳ *Payment abhi tak nahi mili*\n\n"
            "Agar aapne pay kar diya hai to 2-3 minute wait karo aur dobara check karo.\n\n"
            "Problem hai? Support se baat karo 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ========== My Files ==========
async def my_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    access = db.get_user_access(user_id)
    
    if not access or access['expires_at'] <= datetime.now():
        keyboard = [[InlineKeyboardButton("💳 Plan Kharido", callback_data="show_plans")]]
        await query.edit_message_text(
            "🔒 *Aapka koi active plan nahi hai!*\n\n"
            "Plan kharido aur saari files access karo.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    time_left = access['expires_at'] - datetime.now()
    days_left = time_left.days
    hours_left = int(time_left.total_seconds() // 3600) % 24
    
    file_bot_link = f"https://t.me/{config.FILE_BOT_USERNAME}?start=access_{user_id}"
    keyboard = [
        [InlineKeyboardButton("📂 File Bot Kholne Ke Liye Click Karo", url=file_bot_link)],
        [InlineKeyboardButton("🏠 Home", callback_data="back_home")]
    ]
    
    await query.edit_message_text(
        f"✅ *Aapka Plan Active Hai!*\n\n"
        f"⏳ Baaki samay: *{days_left} din, {hours_left} ghante*\n"
        f"📅 Expire: *{access['expires_at'].strftime('%d %b %Y')}*\n\n"
        f"Neeche click karo aur saari files dekho! 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ========== Back Home ==========
async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📦 Plans Dekho & Kharido", callback_data="show_plans")],
        [InlineKeyboardButton("📁 Meri Files", callback_data="my_files")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/YOUR_SUPPORT_USERNAME")]
    ]
    
    await query.edit_message_text(
        "🔐 *Premium Content Access Bot*\n\n"
        "Yahan aap premium files & documents access kar sakte hain.\n"
        "Plan kharido aur apni files unlock karo! 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ========== Main ==========
def main():
    app = Application.builder().token(config.PAYMENT_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="^show_plans$"))
    app.add_handler(CallbackQueryHandler(buy_plan, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(verify_payment_callback, pattern="^verify_"))
    app.add_handler(CallbackQueryHandler(my_files, pattern="^my_files$"))
    app.add_handler(CallbackQueryHandler(back_home, pattern="^back_home$"))
    
    logger.info("Payment Bot chal raha hai...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

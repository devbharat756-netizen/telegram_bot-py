import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import db
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Access check karo
    access = db.get_user_access(user_id)
    has_access = access and access['expires_at'] > datetime.now()
    
    if not has_access:
        keyboard = [[InlineKeyboardButton("💳 Plan Kharido", url=f"https://t.me/{config.PAYMENT_BOT_USERNAME}")]]
        await update.message.reply_text(
            "🔒 *Ye bot sirf premium members ke liye hai!*\n\n"
            "Pehle Payment Bot pe jaao aur plan kharido,\n"
            "phir wapas yahan aao. 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    time_left = access['expires_at'] - datetime.now()
    days_left = time_left.days
    
    # Saari files dikhao
    await show_all_files(update, context, user_id, days_left)

# ========== Saari Files Dikhao ==========
async def show_all_files(update, context, user_id, days_left):
    files = db.get_all_files()
    
    if not files:
        await update.message.reply_text(
            "📭 Abhi koi file available nahi hai.\n"
            "Jald hi nai files aayengi! Stay tuned 🔔"
        )
        return
    
    # Welcome message
    await update.message.reply_text(
        f"✅ *Welcome! Aapka access active hai*\n"
        f"⏳ Baaki: *{days_left} din*\n\n"
        f"📂 *Neeche saari files ki list hai*\n"
        f"Jis file ka preview dekhna ho, uska button dabao 👇",
        parse_mode='Markdown'
    )
    
    # Har file ke liye preview button bhejo
    for file in files:
        emoji = get_file_emoji(file['file_type'])
        keyboard = [[InlineKeyboardButton(f"👁️ Preview Dekho", callback_data=f"preview_{file['id']}")]]
        
        await update.message.reply_text(
            f"{emoji} *{file['title']}*\n"
            f"📝 {file['description']}\n"
            f"📦 Type: {file['file_type'].upper()}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ========== Preview ==========
async def show_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    file_id = query.data.replace("preview_", "")
    
    # Access check
    access = db.get_user_access(user_id)
    if not access or access['expires_at'] <= datetime.now():
        keyboard = [[InlineKeyboardButton("💳 Plan Renew Karo", url=f"https://t.me/{config.PAYMENT_BOT_USERNAME}")]]
        await query.edit_message_text(
            "❌ *Aapka access expire ho gaya!*\n\nPayment bot pe jaake plan renew karo.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    file_data = db.get_file(file_id)
    if not file_data:
        await query.answer("File nahi mili!", show_alert=True)
        return
    
    emoji = get_file_emoji(file_data['file_type'])
    keyboard = [
        [InlineKeyboardButton("📥 File Download Karo", callback_data=f"download_{file_id}")],
        [InlineKeyboardButton("🔙 Back to Files", callback_data="back_to_files")]
    ]
    
    await query.edit_message_text(
        f"{emoji} *{file_data['title']}*\n\n"
        f"📝 *Description:*\n{file_data['description']}\n\n"
        f"📦 *Type:* {file_data['file_type'].upper()}\n"
        f"📅 *Upload Date:* {file_data['upload_date']}\n\n"
        f"File download karne ke liye button dabao 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ========== File Download ==========
async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⏳ File bhej raha hoon...")
    
    user_id = update.effective_user.id
    file_id = query.data.replace("download_", "")
    
    # Access check
    access = db.get_user_access(user_id)
    if not access or access['expires_at'] <= datetime.now():
        keyboard = [[InlineKeyboardButton("💳 Plan Kharido", url=f"https://t.me/{config.PAYMENT_BOT_USERNAME}")]]
        await query.message.reply_text(
            "❌ *Access expire ho gaya!*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    file_data = db.get_file(file_id)
    if not file_data:
        return
    
    # File bhejo
    try:
        if file_data['file_type'] == 'pdf':
            await context.bot.send_document(
                chat_id=user_id,
                document=file_data['telegram_file_id'],
                caption=f"📄 *{file_data['title']}*\n\n⚠️ Ye file aapke plan ke andar accessible hai.",
                parse_mode='Markdown'
            )
        elif file_data['file_type'] == 'video':
            await context.bot.send_video(
                chat_id=user_id,
                video=file_data['telegram_file_id'],
                caption=f"🎥 *{file_data['title']}*\n\n⚠️ Ye file aapke plan ke andar accessible hai.",
                parse_mode='Markdown'
            )
        elif file_data['file_type'] == 'image':
            await context.bot.send_photo(
                chat_id=user_id,
                photo=file_data['telegram_file_id'],
                caption=f"🖼️ *{file_data['title']}*\n\n⚠️ Ye file aapke plan ke andar accessible hai.",
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_document(
                chat_id=user_id,
                document=file_data['telegram_file_id'],
                caption=f"📁 *{file_data['title']}*",
                parse_mode='Markdown'
            )
        
        # Download log karo
        db.log_download(user_id, file_id)
        
    except Exception as e:
        logger.error(f"File bhejne me error: {e}")
        await query.message.reply_text("❌ File bhejne me problem hui. Dobara try karo.")

# ========== Back to Files ==========
async def back_to_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    access = db.get_user_access(user_id)
    days_left = (access['expires_at'] - datetime.now()).days if access else 0
    await show_all_files(update, context, user_id, days_left)

# ========== Admin: File Add Karo ==========
async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Sirf admin ye command use kar sakta hai.")
        return
    
    # Format: /addfile title | description | file_type
    # Phir file bhejo
    if not context.args:
        await update.message.reply_text(
            "📝 *File Add Karne Ka Tarika:*\n\n"
            "1. Pehle ye command do:\n"
            "`/addfile Title | Description | pdf`\n\n"
            "2. Phir turant file bhejo (document/video/image)\n\n"
            "File types: pdf, video, image, doc",
            parse_mode='Markdown'
        )
        return
    
    # Args parse karo
    args_text = ' '.join(context.args)
    parts = args_text.split('|')
    
    if len(parts) < 3:
        await update.message.reply_text("❌ Format galat hai!\n`/addfile Title | Description | file_type`", parse_mode='Markdown')
        return
    
    title = parts[0].strip()
    description = parts[1].strip()
    file_type = parts[2].strip().lower()
    
    # Pending me save karo
    context.user_data['pending_file'] = {
        'title': title,
        'description': description,
        'file_type': file_type
    }
    
    await update.message.reply_text(
        f"✅ Details save ho gayi!\n\n"
        f"📝 Title: *{title}*\n"
        f"📦 Type: *{file_type}*\n\n"
        f"Ab file bhejo (document/video/image) 👇",
        parse_mode='Markdown'
    )

# ========== Admin: File Receive ==========
async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in config.ADMIN_IDS:
        return
    
    pending = context.user_data.get('pending_file')
    if not pending:
        await update.message.reply_text("Pehle /addfile command use karo.")
        return
    
    # File ID nikalo
    telegram_file_id = None
    actual_type = pending['file_type']
    
    if update.message.document:
        telegram_file_id = update.message.document.file_id
        if 'pdf' in update.message.document.mime_type:
            actual_type = 'pdf'
        else:
            actual_type = 'doc'
    elif update.message.video:
        telegram_file_id = update.message.video.file_id
        actual_type = 'video'
    elif update.message.photo:
        telegram_file_id = update.message.photo[-1].file_id
        actual_type = 'image'
    
    if not telegram_file_id:
        await update.message.reply_text("❌ File nahi mili. Document/Video/Photo bhejo.")
        return
    
    # DB me save karo
    file_id = db.add_file(
        title=pending['title'],
        description=pending['description'],
        file_type=actual_type,
        telegram_file_id=telegram_file_id
    )
    
    context.user_data.pop('pending_file', None)
    
    await update.message.reply_text(
        f"✅ *File Successfully Add Ho Gayi!*\n\n"
        f"🆔 File ID: `{file_id}`\n"
        f"📝 Title: *{pending['title']}*\n"
        f"📦 Type: *{actual_type}*\n\n"
        f"Ab ye file saare premium users ko dikhegi! 🎉",
        parse_mode='Markdown'
    )

# ========== Admin: Saari Files List ==========
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        return
    
    files = db.get_all_files()
    if not files:
        await update.message.reply_text("📭 Koi file nahi hai abhi.")
        return
    
    text = "📂 *Saari Files:*\n\n"
    for f in files:
        emoji = get_file_emoji(f['file_type'])
        text += f"{emoji} ID:`{f['id']}` — *{f['title']}* ({f['file_type']})\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ========== Admin: File Delete ==========
async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: `/deletefile FILE_ID`", parse_mode='Markdown')
        return
    
    file_id = context.args[0]
    db.delete_file(file_id)
    await update.message.reply_text(f"✅ File `{file_id}` delete ho gayi!", parse_mode='Markdown')

# ========== Helper ==========
def get_file_emoji(file_type):
    emojis = {'pdf': '📄', 'video': '🎥', 'image': '🖼️', 'doc': '📝'}
    return emojis.get(file_type, '📁')

# ========== Main ==========
def main():
    app = Application.builder().token(config.FILE_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addfile", add_file))
    app.add_handler(CommandHandler("listfiles", list_files))
    app.add_handler(CommandHandler("deletefile", delete_file))
    app.add_handler(CallbackQueryHandler(show_preview, pattern="^preview_"))
    app.add_handler(CallbackQueryHandler(download_file, pattern="^download_"))
    app.add_handler(CallbackQueryHandler(back_to_files, pattern="^back_to_files$"))
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.VIDEO | filters.PHOTO,
        receive_file
    ))
    
    logger.info("File Bot chal raha hai...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

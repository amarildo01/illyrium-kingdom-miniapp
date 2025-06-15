from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import sqlite3

# Database
conn = sqlite3.connect('players.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0
)''')
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute('INSERT OR IGNORE INTO players (user_id) VALUES (?)', (user_id,))
    conn.commit()

    keyboard = [[InlineKeyboardButton("🔥 Tap to Earn!", callback_data='tap')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Illyrium Tap-to-Earn!\nTap the button below to earn points.",
        reply_markup=reply_markup
    )

async def tap_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    cursor.execute('SELECT points FROM players WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    points = row[0] if row else 0
    points += 1  # Add 1 point per tap
    cursor.execute('UPDATE players SET points = ? WHERE user_id = ?', (points, user_id))
    conn.commit()

    await query.answer(text=f"You earned 1 point! Total: {points}")
    keyboard = [[InlineKeyboardButton("🔥 Tap to Earn!", callback_data='tap')]]
    await query.edit_message_text(
        text=f"Total Points: {points}\nKeep tapping!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute('SELECT points FROM players WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    points = row[0] if row else 0
    await update.message.reply_text(f"Your total points: {points}")

if __name__ == '__main__':
    import os
    TOKEN = os.getenv('TELEGRAM_TOKEN')  # Vendos tokenin në environment variable TELEGRAM_TOKEN

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(tap_handler))
    app.add_handler(CommandHandler('balance', balance))

    print("Bot running...")
    app.run_polling()

from telegram.ext import CommandHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database.models import User
from database.db_session import SessionLocal


def start(update: Update, context: CallbackContext):
    session = SessionLocal()
    telegram_id = update.message.from_user.id
    user = session.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            username=update.message.from_user.username,
        )
        session.add(user)
        session.commit()

    # Send welcome message
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("My Servers", callback_data='my_servers')],
        [InlineKeyboardButton("Buy Server", callback_data='buy_server')],
        [InlineKeyboardButton("Profile", callback_data='profile')]
    ])
    update.message.reply_text(
        f"Welcome {user.username}!\nTotal Expenses: {user.total_expenses}\nBalance: {user.balance}",
        reply_markup=reply_markup)

    session.close()


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler("start", start))

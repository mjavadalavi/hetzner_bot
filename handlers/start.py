from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
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
        update.message.reply_text(f"Welcome, {user.first_name}!")
    else:
        update.message.reply_text(f"Welcome back, {user.first_name}!")

    session.close()

def setup_dispatcher(dp):
    dp.add_handler(CommandHandler("start", start))

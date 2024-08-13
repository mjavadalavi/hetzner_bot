from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext
from database.models import User, Server
from database.db_session import SessionLocal
from services.hetzner_service import HetznerService
from services.payment_service import PaymentService

def myservers(update: Update, context: CallbackContext):
    session = SessionLocal()
    telegram_id = update.message.from_user.id
    user = session.query(User).filter(User.telegram_id == telegram_id).first()

    if user:
        total_cost = sum(server.cost_per_hour * 24 * PROFIT_MARGIN for server in user.servers)
        balance = user.balance

        message = f"Total server cost: {total_cost:.2f} USD\nBalance: {balance:.2f} USD\n"
        if not user.servers:
            message += "You have no servers."

        keyboard = [
            [InlineKeyboardButton("View Servers", callback_data='view_servers')],
            [InlineKeyboardButton("Buy New Server", callback_data='buy_new_server')],
            [InlineKeyboardButton("Financial", callback_data='financial')],
            [InlineKeyboardButton("Contact Support", callback_data='support')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)
    else:
        update.message.reply_text("User not found!")

    session.close()

def setup_dispatcher(dp):
    dp.add_handler(CommandHandler("myservers", myservers))

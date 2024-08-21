# main.py
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot.handlers import (
    start,
    servers,
    buy_server,
    select_server,
    confirm_server,
    financial,
    pay_bill,
    download_statement,
    increase_balance,
    increase_balance_payment,
    increase_balance_crypto,
    increase_balance_crypto_confirm,
)
from config import TELEGRAM_TOKEN
from database.db_utils import init_db


def main():
    init_db()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(servers, pattern="^servers$"))
    application.add_handler(CallbackQueryHandler(buy_server, pattern="^buy_server$"))
    application.add_handler(CallbackQueryHandler(select_server, pattern="^country_"))
    application.add_handler(CallbackQueryHandler(confirm_server, pattern="^server_"))

    application.add_handler(CallbackQueryHandler(financial, pattern="^financial$"))
    application.add_handler(CallbackQueryHandler(pay_bill, pattern="^pay_bill$"))
    application.add_handler(CallbackQueryHandler(download_statement, pattern="^download_statement$"))

    application.add_handler(CallbackQueryHandler(increase_balance, pattern="^increase_balance$"))
    application.add_handler(CallbackQueryHandler(increase_balance_payment, pattern="^increase_balance_payment$"))
    application.add_handler(CallbackQueryHandler(increase_balance_crypto, pattern="^increase_balance_crypto$"))
    application.add_handler(
        CallbackQueryHandler(increase_balance_crypto_confirm, pattern="^increase_balance_crypto_confirm_"))

    application.run_polling()


if __name__ == "__main__":
    main()
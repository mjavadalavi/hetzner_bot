from telegram.ext import Updater

import config
from handlers import start, servers


def main():
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    start.setup_dispatcher(dp)
    servers.setup_dispatcher(dp)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

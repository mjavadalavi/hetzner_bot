import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HETZNER_API_KEY = os.getenv("HETZNER_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SUPPORT_CHANNEL_ID = os.getenv("SUPPORT_CHANNEL_ID")
BOT_FEE_COEFFICIENT = float(os.getenv("BOT_FEE_COEFFICIENT", 1.1))
ZARINPAL_MERCHANT_ID = os.getenv("ZARINPAL_MERCHANT_ID")
ZIBAL_MERCHANT_ID = os.getenv("ZIBAL_MERCHANT_ID")
PAYMENT_CALLBACK_URL = os.getenv("PAYMENT_CALLBACK_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
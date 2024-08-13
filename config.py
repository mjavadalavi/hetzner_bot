from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HETZNER_API_TOKEN = os.getenv("HETZNER_API_TOKEN")
ZIBAL_API_KEY = os.getenv("ZIBAL_API_KEY")
ZARINPAL_API_KEY = os.getenv("ZARINPAL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
PROFIT_MARGIN = float(os.getenv("PROFIT_MARGIN", 1.2))
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

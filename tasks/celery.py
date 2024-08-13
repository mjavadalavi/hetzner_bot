from celery import Celery
from config import CELERY_BROKER_URL
from celery.schedules import crontab

celery_app = Celery('hetzner_bot', broker=CELERY_BROKER_URL)
celery_app.conf.update(
    result_backend=CELERY_BROKER_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    'process-billing-every-hour': {
        'task': 'tasks.billing.process_billing',
        'schedule': crontab(minute=0, hour='*'),
    },
}

from celery import Celery
from config import CELERY_BROKER_URL

celery_app = Celery('hetzner_bot', broker=CELERY_BROKER_URL)
celery_app.conf.update(
    result_backend=CELERY_BROKER_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

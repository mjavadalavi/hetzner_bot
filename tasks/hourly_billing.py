from celery import Celery
from celery.schedules import crontab

from database.db_utils import get_db
from database.models import User, Server, Transaction
from datetime import datetime
from config import REDIS_URL, BOT_FEE_COEFFICIENT
from services.hetzner_api import delete_server

app = Celery('tasks', broker=REDIS_URL)


@app.task
def process_hourly_billing():
    db = next(get_db())
    servers = db.query(Server).filter(Server.status == 'active').all()

    for server in servers:
        user = server.user
        hourly_cost = server.hourly_cost * BOT_FEE_COEFFICIENT

        if user.balance >= hourly_cost:
            user.balance -= hourly_cost
            transaction = Transaction(
                user_id=user.id,
                amount=-hourly_cost,
                type="usage",
                timestamp=datetime.utcnow()
            )
            db.add(transaction)
        else:
            server.status = 'reserved'
            server.reserved_until = datetime.utcnow() + timedelta(days=1)

    db.commit()


@app.task
def check_reserved_servers():
    db = next(get_db())
    reserved_servers = db.query(Server).filter(Server.status == 'reserved').all()

    for server in reserved_servers:
        if datetime.utcnow() > server.reserved_until:
            delete_server(server.hetzner_id)
            db.delete(server)

    db.commit()


app.conf.beat_schedule = {
    'process-hourly-billing': {
        'task': 'tasks.hourly_billing.process_hourly_billing',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'check-reserved-servers': {
        'task': 'tasks.hourly_billing.check_reserved_servers',
        'schedule': crontab(minute=0, hour=0),  # Run daily
    },
}
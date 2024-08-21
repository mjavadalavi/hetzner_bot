from tasks.celery import celery_app
from database.db_utils import SessionLocal
from database.models import User
from config import PROFIT_MARGIN

@celery_app.task
def process_billing():
    session = SessionLocal()
    users = session.query(User).all()
    for user in users:
        for server in user.servers:
            hourly_cost = server.cost_per_hour * PROFIT_MARGIN
            if user.balance >= hourly_cost:
                user.balance -= hourly_cost
                session.commit()
            else:
                # Optionally handle insufficient balance
                pass
    session.close()

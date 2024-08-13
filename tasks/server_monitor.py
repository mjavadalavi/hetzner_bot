@celery_app.task
def monitor_servers():
    session = SessionLocal()
    # logic to monitor servers, e.g., check if they are up and running
    session.close()

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import dollar_rate
from .database import get_db

def start_scheduler():
    scheduler = BackgroundScheduler()
    db_session = next(get_db())
    scheduler.add_job(dollar_rate, CronTrigger(hour=14, minute=0), args=[db_session])
    scheduler.start()
    print("Scheduler started!")
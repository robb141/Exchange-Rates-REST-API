from celery import Celery
from celery.schedules import crontab

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

app = Celery(
    "cron_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["cron_tasks.download_rates"],
)

app.conf.beat_schedule = {
    "everyday-task": {
        "task": "cron_tasks.download_rates.download_rates",
        "schedule": crontab(hour=0, minute=1),
    }
}

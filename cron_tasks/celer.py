from celery import Celery
from celery.schedules import crontab

app = Celery("cron_tasks", include=["cron_tasks.download_rates"])


app.conf.beat_schedule = {
    "everyday-task": {
        "task": "cron_tasks.download_rates.download_rates",
        "schedule": crontab(hour=0, minute=1),
    }
}

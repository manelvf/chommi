import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chommies.settings")

app = Celery("chommies")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'check-expired-subscriptions-daily': {
        'task': 'bets.tasks.check_expired_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}

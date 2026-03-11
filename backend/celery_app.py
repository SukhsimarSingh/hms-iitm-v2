from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(__name__)

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Celery Beat Schedule - for recurring tasks
celery_app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'backend.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    'generate-monthly-reports': {
        'task': 'backend.tasks.generate_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),  # 1st of month at 8 AM
    },
}

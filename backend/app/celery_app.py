from celery import Celery
from celery.schedules import crontab
from app.config import Config


def make_celery(app=None):
    celery = Celery(
        app.import_name if app else 'quizzo',
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.services.celery_tasks']  # Updated to services folder
    )

    # Update configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='IST',
        enable_utc=True,
        beat_schedule={
            'send-daily-reminders': {
                'task': 'app.services.celery_tasks.send_daily_reminders_task',
                'schedule': crontab(hour=11, minute=32),  
            },
            'send-monthly-reports': {
                'task': 'app.services.celery_tasks.send_monthly_reports_task',
                'schedule': crontab(day_of_month=1, hour=11, minute=30),
            },
        },
        # Additional Celery settings
        task_routes={
            'app.services.celery_tasks.send_daily_reminders_task': {'queue': 'email'},
            'app.services.celery_tasks.send_monthly_reports_task': {'queue': 'email'},
            'app.services.celery_tasks.send_individual_daily_reminder_task': {'queue': 'email'},
            'app.services.celery_tasks.send_individual_monthly_report_task': {'queue': 'email'},
            'app.services.celery_tasks.schedule_user_emails_task': {'queue': 'default'},
        },
        task_default_queue='default',
        task_default_exchange='default',
        task_default_exchange_type='direct',
        task_default_routing_key='default',
    )

    if app:
        class ContextTask(celery.Task):

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery

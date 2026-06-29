import os
from celery import Celery
from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amaliyot_project.settings')


app = Celery('amaliyot_project')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()


app.conf.beat_schedule = {
    'auto-finish-tests-every-minute': {
        'task': 'amaliyot.tasks.auto_finish_expired_tests',
        'schedule': crontab(),  
    },
}


import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
app = Celery('shop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# celery -A shop worker -l info -P eventlet
# celery -A shop beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

import os
from flowers_project.flowers_project.celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

app = Celery('Flowers_Django_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
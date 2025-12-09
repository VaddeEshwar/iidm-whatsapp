# D:\Mamatha_P\msg_proj\bulk_whatsapp\bulk_whatsapp\celery.py

import os
from celery import Celery
from kombu import Queue

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bulk_whatsapp.settings')

# Create Celery app
app = Celery('bulk_whatsapp')

# Load config from Django settings (using CELERY namespace)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps (like 'sms.tasks')
app.autodiscover_tasks()

app.conf.task_queues = (
    Queue('whatsapp', routing_key='whatsapp'),
)

app.conf.task_default_queue = 'whatsapp'
app.conf.task_default_exchange = 'whatsapp'
app.conf.task_default_routing_key = 'whatsapp'

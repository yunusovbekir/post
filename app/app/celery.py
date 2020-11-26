from __future__ import absolute_import
import os
from django.conf import settings
from celery import Celery

settings_file = 'settings.py'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

project_name = 'app'

app = Celery(project_name)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if settings.PROD:
    redis_host = 'redis'
else:
    redis_host = 'localhost'

REDIS_CONNECTION = '{protocol}://{host}:{port}'.format(
    protocol=os.environ.get('REDIS_PROTOCOL', 'redis'),
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=os.environ.get('REDIS_PORT', '6379'),
)

CELERY_CONFIG = dict(
    BROKER_URL='{redis}/0'.format(redis=REDIS_CONNECTION),
    CELERYBEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
    CELERY_RESULT_BACKEND='{redis}/1'.format(redis=REDIS_CONNECTION),
    CELERY_DISABLE_RATE_LIMITS=True,
    CELERY_IGNORE_RESULT=True,
    CELERY_ACCEPT_CONTENT=['json', ],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE='Asia/Baku',
    CELERY_IMPORTS=[
        "app.tasks",
    ],
)
# if settings.PROD:
#     CELERY_CONFIG['BROKER_USE_SSL'] = {
#         'ssl_cert_reqs': ssl.CERT_NONE
#     }

app.conf.update(**CELERY_CONFIG)

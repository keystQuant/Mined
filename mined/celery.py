from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.signals import celeryd_after_setup
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mined.settings')

app = Celery('mined')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@celeryd_after_setup.connect
def after_setup(sender=None, body=None, **kwargs):
    pass

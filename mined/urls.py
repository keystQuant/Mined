from django.conf.urls import include, url
from django.contrib import admin

from .views import test

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Celery 제대로 작동하는지 테스트용 URL
    url(r'^mined-test/$', test, name='test'),

    # API URL
    url(r'^mined/api/v1/', include('api.urls', namespace='api')),
]

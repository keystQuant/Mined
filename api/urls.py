from django.conf.urls import url

from api.views import TaskAPIView

urlpatterns = [
    url(r'^$', TaskAPIView.as_view(), name='task'),
]

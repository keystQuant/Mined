from django.urls import path

from api.views import TaskAPIView, TestAPIView

urlpatterns = [
    path('test/', TestAPIView.as_view(), name='test'),
    path('', TaskAPIView.as_view(), name='task'),
]

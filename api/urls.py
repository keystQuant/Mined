from django.urls import path

from api.views import GatewayView, TaskAPIView, TestAPIView

urlpatterns = [
    path('test/', TestAPIView.as_view(), name='test'),
    path('', TaskAPIView.as_view(), name='task'),
    path('task/', GatewayView.as_view(), name='test'),
]

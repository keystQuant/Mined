from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

class TestAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data
        result = {'status': 'GOOD'}
        return Response(result, status=200)

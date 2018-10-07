from django.http import JsonResponse
from django.views.generic import View

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from algorithms.marketsignal import MarketSignalProcessor
from algorithms.portfolio import PortfolioProcessor
from algorithms.rms import RMSProcessor
from algorithms.scanner import ScannerProcessor


from .reducers import Reducers

class GatewayView(View):
    def get(self, request):
        action_type = request.GET.get('type')
        env_type = request.GET.get('env')
        if not env_type:
            # 테스팅할 때는 local이라고 env_type을 넣어줘야한다
            env_type = 'remote'
        reducer_inst = Reducers(action_type, env_type)

        if reducer_inst.has_reducer():
            status = reducer_inst.reduce()
            if status == True:
                return JsonResponse({'status': 'DONE'}, json_dumps_params={'ensure_ascii': True})
            elif status == False:
                return JsonResponse({'status': 'FAIL'}, json_dumps_params={'ensure_ascii': True})
        else: # 리듀서가 존재하지 않는다면
            return JsonResponse({'status': 'NO ACTION: {}'.format(action_type)}, json_dumps_params={'ensure_ascii': True})


# *** UPDATE: 20180806 ***#
class TestAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        result = {'status': 'GOOD'}
        return Response(result, status=status.HTTP_200_OK)


# *** UPDATE: 20180806 ***#
class TaskAPIView(APIView):
    # 레퍼런스: http://www.django-rest-framework.org/api-guide/status-codes/ (status code)

    ## /mined/api/<version>/?algorithm=<algorithm>&task=<taskname> ##
    # version: v1
    # algorithm: MARKET, SCANNER, PORTFOLIO, RMS
    # taskname: i.e. BM_INFO, SIZE_INFO etc.
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        algorithm = request.GET.get('algorithm')
        task = request.GET.get('task')

        ##### 모든 태스크 클래스는 리듀서를 불러서 result 값을 받아야 합니다 #####
        ##### ALGO #1 #####
        if algorithm == 'MARKET':
            task_class = MarketSignalProcessor(task)
            result = task_class.reduce()
        ##### ALGO #2 #####
        elif algorithm == 'SCANNER':
            task_class = ScannerProcessor(task)
            result = task_class.reduce()
        ##### ALGO #3 #####
        elif algorithm == 'PORTFOLIO':
            portfolio_type = request.GET.get('portfolio_type')
            stocks = request.GET.get('stocks').split(',')
            capital = float(request.GET.get('capital'))
            task_class = PortfolioProcessor(task, portfolio_type, stocks, capital)
            result = task_class.reduce()
        ##### ALGO #4 #####
        elif algorithm == 'RMS':
            task_class = RMSProcessor(task)
            result = task_class.reduce()
        else:
            # 받은 알고리즘 값이 존재하지 않는 알고리즘이면 '없는 알고리즘'이라고 리턴
            result = '없는 알고리즘'

        # 위에서 받은 result 값을 result_json에 result키값으로 넣어준다
        if result == '없는 알고리즘':
            result_json = {'status': 'FAIL', 'result': result}
            return Response(result_json, status=status.HTTP_400_BAD_REQUEST)
        else:
            result_json = {'status': 'GOOD', 'result': result}
            return Response(result_json, status=status.HTTP_200_OK)

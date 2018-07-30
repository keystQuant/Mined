from django.http import JsonResponse

from algorithms.tasks import test_task

def test(request):
    try:
        test_task.delay()
    except:
        print('error')
    responseData = {
        'status': 'SUCCESS'
    }
    return JsonResponse(responseData)

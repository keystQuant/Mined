from __future__ import absolute_import, unicode_literals
from celery.decorators import task

@task(name="test_task")
def test_task():
    try:
        num = 1
        second_num = 2
        sum = num + second_num
        print(sum)
    except:
        print('error')
    return (True, sum)

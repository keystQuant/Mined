'''
Mined. Test

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import pytest

from django.test import TestCase
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient

from algorithms.marketsignal import MarketSignalProcessor


class MarketSignalTestCase(TestCase):
    '''
    마켓시그널 유닛 테스트:

    마켓시그널 모듈 (MarketSignalProcessor) 안에 있는 함수들을 하나씩 테스트한다
    1. calc_bm_info()
    2. get_size_info()
    3. get_style_info()
    4. get_industry_info()
    5. make_rank_data()
    '''

    def setUp(self):
        # 모든 테스트를 시작하기 전에 MarketSignalProcessor 인스턴스를 만들어서
        # 데이터를 로드할 필요가 있다
        self.ms = MarketSignalProcessor()

        # 데이트값을 안 넣었기 때문에 오늘 날짜로 자동 새팅되야 한다
        # 테스트해본다
        today_date = datetime.now().strftime('%Y%m%d')
        self.assertEqual(self.ms.today_date, today_date, msg='날짜가 제대로 새팅되지 않았다')


        self.client = APIClient(enforce_csrf_checks=True)
        self.username = 'lee'
        self.email = 'lee@gmail.com'
        self.password = '123123123'
        # create new user to send post requests
        self.user = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
        }

        # 테스트영 user-data 생성
        self.userdata =  {
            'username': self.username,
            'password': self.password,
        }
        # create sentece data
        self.word = {
                    'owner':'VA',
                    'username':'',
                    'source':'TED',
                    'role':'프레젠테이션',
                    'word':'speak',
                    'translated':'말하다',
                    }


        response = self.client.post(
            URL['user_create_url'],
            self.user,
            format='json'
        )
        self.assertEqual(User.objects.all().count(), 1, msg='user data not created properly')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.first().username, self.user['username'])
        self.assertEqual(User.objects.first().email, self.user['email'])

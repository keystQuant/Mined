'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import pytest

from django.core.cache import cache


## Test 시작 ##
@pytest.fixture
def cache_data():
    cache_data = '장고 캐시 데이터'
    res = cache.set('test_cache_key', cache_data)
    assert res == True # 캐시 데이터를 저장할 수 있다
    return cache_data

def test_cache_can_get_and_delete_key(cache_data):
    value = cache.get('test_cache_key')
    assert value == cache_data

    res = cache.delete('test_cache_key')
    assert res == True

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIClient

from rest_framework_jwt import utils, views
from rest_framework_jwt.compat import get_user_model
from rest_framework_jwt.settings import api_settings, DEFAULTS

import json, os
from django.utils.encoding import smart_text
from services.models import Word
from accounts.models import Profile
User = get_user_model()

from tests.url_endpoints import URL

class WordAPITestCase(TestCase):
    '''
    Word REST API testing module
    '''

    def setUp(self):
        print('Starting Word API test')
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

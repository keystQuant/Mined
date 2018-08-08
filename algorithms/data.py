'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import requests
import redis
import pandas as pd

from mined.settings import CACHE_IP as IP

from cryptography.fernet import Fernet
from mined.crypt_key import KEY

cipher_suite = Fernet(KEY)

cache_pw = b'gAAAAABbY9rwNjWChyC-LgHSh64oczJaJqf67T8lcceZ93Bda4v-1AG8xCU7zoLIyArDwfaTLpm4fQuBdJpyhASfZLABdfhKTsKH14WPj48HvjObgc9jltGLWFNWkHBMbmCWzq8J9G64jC-gkcrXz2hGOZ-rFewWbeuMMeYSJ4u_LIxFBfUREl4='
PW = cipher_suite.decrypt(cache_pw).decode()

DATA_MAPPER = {
    'index_tickers': 'INDEX_TICKERS',
    'kospi_tickers': 'KOSPI_TICKERS',
    'kosdaq_tickers': 'KOSDAQ_TICKERS',
    'index': '_INDEX',
    'ohlcv': '_OHLCV'
}

MARKET_CODES = {
    # 시장 인덱스
    '코스피': 'I.001',
    '코스닥': 'I.201',

    # 사이즈 인덱스
    '코스피 대형주': 'I.002',
    '코스피 중형주': 'I.003',
    '코스피 소형주': 'I.004',
    '코스닥 대형주': 'I.202',
    '코스닥 중형주': 'I.203',
    '코스닥 소형주': 'I.204',

    # 스타일 인덱스
    '성장주': 'I.431', # KRX 스마트 모멘텀
    '가치주': 'I.432', # KRX 스마트 밸류
    '배당주': 'I.192', # KRX 고배당 50
    '퀄리티주': 'I.433', # KRX 스마트 퀄리티
    '사회책임경영주': 'I.426', # KRX 사회책임경영

    # 산업 인덱스
    '코스피 음식료품': 'I.005',
    '코스피 섬유,의복': 'I.006',
    '코스피 종이,목재': 'I.007',
    '코스피 화학': 'I.008',
    '코스피 의약품': 'I.009',
    '코스피 비금속광물': 'I.010',
    '코스피 철강및금속': 'I.011',
    '코스피 기계': 'I.012',
    '코스피 전기,전자': 'I.013',
    '코스피 의료정밀': 'I.014',
    '코스피 운수장비': 'I.015',
    '코스피 유통업': 'I.016',
    '코스피 전기가스업': 'I.017',
    '코스피 건설업': 'I.018',
    '코스피 운수창고': 'I.019',
    '코스피 통신업': 'I.020',
    '코스피 금융업': 'I.021',
    '코스피 은행': 'I.022',
    '코스피 증권': 'I.024',
    '코스피 보험': 'I.025',
    '코스피 서비스업': 'I.026',
    '코스피 제조업': 'I.027',
    '코스닥 기타서비스': 'I.212',
    '코스닥 IT종합': 'I.215',
    '코스닥 제조': 'I.224',
    '코스닥 건설': 'I.226',
    '코스닥 유통': 'I.227',
    '코스닥 운송': 'I.229',
    '코스닥 금융': 'I.231',
    '코스닥 오락, 문화': 'I.237',
    '코스닥 통신방송서비스': 'I.241',
    '코스닥 IT S/W & SVC': 'I.242',
    '코스닥 IT H/W': 'I.243',
    '코스닥 음식료,담배': 'I.256',
    '코스닥 섬유,의류': 'I.258',
    '코스닥 종이,목재': 'I.262',
    '코스닥 출판,매체복제': 'I.263',
    '코스닥 화학': 'I.265',
    '코스닥 제약': 'I.266',
    '코스닥 비금속': 'I.267',
    '코스닥 금속': 'I.268',
    '코스닥 기계,장비': 'I.270',
    '코스닥 일반전기,전자': 'I.272',
    '코스닥 의료,정밀기기': 'I.274',
    '코스닥 운송장비,부품': 'I.275',
    '코스닥 기타 제조': 'I.277',
    '코스닥 통신서비스': 'I.351',
    '코스닥 방송서비스': 'I.352',
    '코스닥 인터넷': 'I.353',
    '코스닥 디지탈컨텐츠': 'I.354',
    '코스닥 소프트웨어': 'I.355',
    '코스닥 컴퓨터서비스': 'I.356',
    '코스닥 통신장비': 'I.357',
    '코스닥 정보기기': 'I.358',
    '코스닥 반도체': 'I.359',
    '코스닥 IT부품': 'I.360'
}

##### 레디스에서 Pandas DF 데이터 가져오는 방법:
##### r = redis.Redis(host=IP, port=6379, password=PW)
##### response = pd.read_msgpack(r.get(key)) <-- DataFrame이면 이렇게 가져오는 것이 가능

class Data:

    def __init__(self, algorithm_type=None):
        print('Connecting to cache server (Redis) on Gobble server')
        print('Cache at {}'.format(IP))
        self.redis_client = redis.StrictRedis(host=IP, port=6379, password=PW)

        if algorithm_type == 'marketsignal':
            print('marketsignal')
        elif algorithm_type == 'portfolio':
            print('portfolio')
        elif algorithm_type == 'rms':
            print('rms')
        else:
            print('none')

    #*** UPDATE: 20180808 ***#
    #*** ISSUES: NONE ***#
    def get_val(self, key):
        ## mined에서 사용하게 될 모든 데이터는 TICKERS 데이터가 아니면 pandas df이다
        ## TICKERS 데이터는 리스트 형식이다
        if 'TICKERS' in key:
            data = self.redis_client.lrange(key, 0, -1)
            data = list(map(lambda x: x.decode('utf-8'), data))
        else:
            data = pd.read_msgpack(self.redis_client.get(key))
        return data

    def set_tickers(self):
        tickers_key = DATA_MAPPER['tickers']
        response = self.redis_client.lrange(tickers_key, 0, -1)
        response = list(map(lambda x: x.decode('utf-8'), response))
        self.tickers = response

    def get_ohlcv(self, ticker):
        if self.tickers == None:
            self.set_tickers()
        # if ticker in self.tickers:

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

# 미래에 레디스 키 이름이 바뀔 수 있기 때문에 아래와 같이 키값들을 하나의 딕셔너리 안에 모아 관리한다
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
    """
    Data 객체를 사용하고 싶다면, Data 인스턴스를 생성할 때 algorithm_type을 넣어줘야 한다.
    algorithm_type은 marketsignal, portfolio, rms, scanner 이렇게 4가지가 있고,

    * 마켓시그널 알고리즘 계산에 필요한 데이터는 benchmark(bm), size, style, industry 인덱스 데이터이다.
    * 포트폴리오 알고리즘에 필요한 데이터는 선택된 종목의 최근 종가 정보이다.
    * RMS 알고리즘에 필요한 데이터는 선택된 종목 리스트의 종가 데이터 그리고 코스피 지수의 인덱스 정보이다 (5년).
    * Scanner 알고리즘에 필요한 데이터는

    인스턴스를 생성할 때 algorithm_type을 넣어주면 request 메소드를 사용하여,
    원하는 정보를 요청할 수 있게 된다.

    예를 들어서,

    data = Data('marketsignal')
    data.request('bm')
    
    이라고 인스턴스를 생성하고 'bm' 정보를 요청하면, 코스피, 코스닥 데이터가 담긴 Pandas DataFrame이 속성으로 새팅된다.
    """

    def __init__(self, algorithm_type=None):
        print('Connecting to cache server (Redis) on Gobble server')
        print('Cache at {}'.format(IP))
        # 데이터가 있는 레디스 캐시로 연결
        self.redis_client = redis.StrictRedis(host=IP, port=6379, password=PW)
        self.algorithm_type = algorithm_type

        if algorithm_type == 'marketsignal':
            self.set_index_lists() # 알고리즘 타입을 마켓시그널로 정의내리고 시작하면, set_index_lists를 불러준다

            ### 마켓시그널 알고리즘에서는 MARKET_CODES에 있는 모든 종목의 데이터가 필요하다 ###
            # 인덱스 데이터를 가져온다
            self.tickers = self.get_val(DATA_MAPPER['index_tickers'])

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
            data = pd.read_msgpack(self.redis_client.get(key)) # 레디스에서 df 형식의 데이터를 가지고 오는 방법
        return data

    #*** UPDATE: 20180809 ***#
    def set_index_lists(self):
        index_list = MARKET_CODES.keys() # 인덱스 종류를 담은 리스트

        # 모든 인덱스 종류를 담은 리스트
        # 산업별 분류는 너무 많아서 나머지 리스트에서 없는 인덱스를 가져오는 방식으로 리스트 정의
        self.bm = ['코스피', '코스닥']
        self.size = ['코스피 대형주', '코스피 중형주', '코스피 소형주', '코스닥 대형주', '코스닥 중형주', '코스닥 소형주']
        self.style = ['성장주', '가치주', '배당주', '퀄리티주', '사회책임경영주']
        self.industry = [index for index in index_list if index not in self.bm and \
                                                          index not in self.size and \
                                                          index not in self.style]

        print('BM: ' + ' '.join(str(i) for i in self.bm))
        print('SIZE: ' + ' '.join(str(i) for i in self.size))
        print('STYLE: ' + ' '.join(str(i) for i in self.style))
        print('INDUSTRY: ' + ' '.join(str(i) for i in self.industry))

    #*** UPDATE: 20180809 ***#
    def make_index_data(self, index_type):
        index_data_dict = {} # 딕셔너리 형식으로 저장한다
        # Marketsignal 알고리즘에 필요한 데이터
        # index_type가 뭔지에 따라 루프 돌려 불러올 데이터의 리스트가 다르다
        if index_type == 'bm':
            index_list = self.bm

        elif index_type == 'size':
            index_list = self.size

        elif index_type == 'style':
            index_list = self.style

        elif index_type == 'industry':
            index_list = self.industry

        for index in index_list:
            # 레디스 키값은 I.002_INDEX와 같은 형식이다
            index_key = MARKET_CODES[index] + DATA_MAPPER['index'] # MARKET_CODES 딕셔너리에서 코드를 찾아온다
            index_df = self.get_val(index_key)
            index_data_dict[index] = index_df
        return index_data_dict

    #*** UPDATE: 20180809 ***#
    def request(self, data_type):
        # 데이터를 요청하면 Data 객체내에서 데이터를 가공한 다음 값을 사용할 수 있도록 요청한 속성들을 만들어 준다
        algorithm_type = self.algorithm_type

        if algorithm_type == 'marketsignal':
            if data_type == 'bm':
                # 'bm'으로 make_index_data를 한다
                # 그리고 리턴된 딕셔너리에서 코스피와 코스닥을 각각 kospi_index와 kosdaq_index에 부여한다
                bm_data = self.make_index_data(data_type)
                self.kospi_index = bm_data['코스피']
                self.kosdaq_index = bm_data['코스닥']
            elif data_type == 'size':
                pass
            elif data_type == 'style':
                pass
            elif data_type == 'industry':
                pass

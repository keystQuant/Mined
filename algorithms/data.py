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

    이런 방식으로 데이터를 불러오는 이유는 알고리즘 계산에 필요한 데이터만 그때그때 가져오기 위함이다.
    """

    def __init__(self, algorithm_type=None, stocks=None):
        # 어떤 알고리즘에 사용되는 데이터 요청을 보낼건지 알려준다
        # 어떤 주식 종목 데이터를 요청할건지 알려준다
        # algorithm_type이나 stocks 정보를 안 넣어줘도 된다
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
            if stocks != None:
                self.port_stocks = stocks
            else:
                self.port_stocks = [] # stocks를 인자로 받지 않으면 빈 리스트를 부여한다
            # 포트폴리오 알고리즘에 필요한 데이터는 stocks리스트 안에 있는 주식 데이터이다

        elif algorithm_type == 'rms':
            # RMS 알고리즘에는 전체 종목 점수를 매겨 랭킹을 매기는 알고리즘이 있다
            # 그 알고리즘을 돌리기 위해서는 코스피, 코스닥 종목 리스트가 필요하다
            self.set_tickers_list()

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

    #*** UPDATE: 20180814 ***#
    def set_tickers_list(self):
        # RMS 알고리즘에 필요한 코스피, 코스닥 코드 정보를 리스트로 만든다
        self.kospi_tickers = self.get_val(DATA_MAPPER['kospi_tickers'])
        self.kosdaq_tickers = self.get_val(DATA_MAPPER['kosdaq_tickers'])

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

    #*** UPDATE: 20180814 ***#
    def make_ohlcv_data(self):
        # 포트폴리오에 필요한 데이터는 포트폴리오에 포함되어 있는 종목이다
        # RMS에 필요한 데이터는 코스피, 코스닥 모든 종목 데이터이다
        if self.algorithm_type == 'portfolio':
            stock_list = self.port_stocks

        elif self.algorithm_type == 'rms':
            stock_list = self.kospi_tickers + self.kosdaq_tickers

            # RMS 데이터는 코스피, 코스닥 종목 갯수로 리스트를 나누어 리턴한다
            # 그러기 위해서는 코스피와 코스닥 전체 종목 수를 알아야한다
            kp_count = len(self.kospi_tickers)
            kd_count = len(self.kosdaq_tickers) # 없어도됨!

        # 데이터 요청을 보내어 리턴되는 DF들을 리스트 안에 넣는다
        ohlcv_data_list = []
        for stock in stock_list:
            ohlcv_key = stock + DATA_MAPPER['ohlcv'] # 000020_OHLCV와 같은 형식
            ohlcv_df = self.get_val(ohlcv_key)
            ohlcv_data_list.append(ohlcv_df)

        if self.algorithm_type == 'rms':
            # RMS용 데이터면 리스트를 두개로 나누어서 리턴한다
            # 첫 번째 리스트는 코스피 정보를 모은 리스트이고,
            # 두 번째 리스트는 코스닥 정보를 모은 리스트이다.
            ohlcv_data_list = [ohlcv_data_list[:kp_count], ohlcv_data_list[kp_count:]]

        return ohlcv_data_list

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
                size_data = self.make_index_data(data_type)
                self.kp_lg_cap_index = size_data['코스피 대형주']
                self.kp_md_cap_index = size_data['코스피 중형주']
                self.kp_sm_cap_index = size_data['코스피 소형주']
                self.kd_lg_cap_index = size_data['코스닥 대형주']
                self.kd_md_cap_index = size_data['코스닥 중형주']
                self.kd_sm_cap_index = size_data['코스닥 소형주']
            elif data_type == 'style':
                style_data = self.make_index_data(data_type)
                self.growth_index = style_data['성장주']
                self.value_index = style_data['가치주']
                self.yield_index = style_data['배당주']
                self.quality_index = style_data['퀄리티주']
                self.social_index = style_data['사회책임경영주']
            elif data_type == 'industry':
                industry_data = self.make_index_data(data_type)
                self.industry_data = industry_data

        elif algorithm_type == 'portfolio':
            pass

        elif algorithm_type == 'rms':
            pass

'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.test import TestCase

from algorithms.portfolio import PortfolioProcessor


class PortfolioTestCase(TestCase):
    def test_get_recent_stock_close_price(self):
        p = PortfolioProcessor('get_recent_stock_close_price', 'S', ['000020', '000030', '005930'], 10000000)
        test_stock = '000020'
        result = p.get_recent_stock_close_price(test_stock)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)

# ## Data 객체 Test 시작 ##
# @pytest.fixture
# def example_S_portfolio_data():
#     portfolio_type = 'S' # 주식형 포트폴리오
#     stocks = ['000020', '000030', '005930']
#     capital = 10000000 # 기본 자본금 1000만원
#     # 포트폴리오 프로세서 생성
#     p = PortfolioProcessor(portfolio_type, stocks, capital)
#     return p
#
# ### 객체 생성 테스트 ###
# def test_processor_can_create_port_metadata(example_S_portfolio_data):
#     # 예시 포트폴리오를 생성한다
#     p = example_S_portfolio_data
#     # p.port_params가 제대로 만들어졌는지 테스트한다
#     assert type(p.port_params) == dict # 데이터타입 확인
#     assert p.port_params['portfolio'] == 'S'
#
#     # capital_per_stock이 float가 아니고 integer인지 확인
#     assert type(p.port_params['capital_per_stock']) == int
#
# def test_processor_gets_ohlcv_data_from_data_inst(example_S_portfolio_data):
#     p = example_S_portfolio_data
#     # Data 인스턴스로 요청을 보내서 제대로된 리스트 형식의 데이터를 가져오는지 확인
#     assert type(p.ohlcv_inst_list) == list
#
# def test_processor_can_get_recent_stock_close_price(example_S_portfolio_data):
#     p = example_S_portfolio_data
#     test_stock = '000020'
#     close_price = p.get_recent_stock_close_price(test_stock)
#     assert type(close_price) == int

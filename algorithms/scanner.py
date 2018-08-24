'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.utils import timezone
import numpy as np
import pandas as pd

from algorithms.data import Data


class ScannerPreProcessor:

    # *** UPDATE: 20180801 ***#
    def __init__(self, today_date=None):
        # 오늘 날짜를 인자로 받고, 아무값이 들어오지 않았다면 YYYYMMDD형식으로 직접 포맷하여
        # self.today_date로 새팅
        if today_date == None:
            self.today_date = timezone.now().strftime('%Y%m%d')
        else:
            self.today_date = today_date

        # 데이터베이스 혹은 캐시에서 데이터를 가져올 수 있도록 Data 인스턴스를 만들어준다.
        # 어떤 데이트를 필요로 하는지 알기 위해 'scanner'을 인자로 보내준다.
        self.data = Data('scanner')

    # *** UPDATE: 20180801 ***#
    def calc_supply_demand(self, ticker):
        data = self.data
        ticker_data = data.get_scanner_data(ticker)

        OHLCV = ticker_data.ohlcv
        BUY_DATA = ticker_data.buy
        NET_BUYSELL = ticker_data.net_buysell

        # pandas로 계산
        BUYSELL['code'] = BUYSELL['code'].apply(lambda x: str(x).zfill(6))
        BUYSELL = BUYSELL.set_index(['date', 'code'])

        # 레이블:
        # private - 개인 투자자
        # forgn - 외국인 투자자
        # inst_sum - 기관 투자자
        # etc_inst - 기타법인
        labels = ['private_b', 'forgn_b', 'inst_sum_b', 'etc_inst_b', 'private_n', 'forgn_n', 'inst_sum_n', 'private_n']
        BUYSELL = BUYSELL[labels]

        OHLCV['code'] = OHLCV['code'].apply(lambda x: str(x).zfill(6))
        OHLCV = OHLCV[(OHLCV['date'] > 20060101) & (OHLCV['date'] < 20180215)]
        OHLCV = OHLCV.set_index(['date', 'code'])

        scanner_data = pd.concat([BUYSELL, OHLCV], axis=1)
        scanner_data = scanner_data.reset_index('code')
        scanner_data.index = pd.to_datetime(scanner_data.index, format='%Y%m%d')

    def agent_possession(self, ticker):
        # calculate possession & total total_stock_in_circulation
        for agent in ['individual','foreign_retail','institution','etc_corporate','trust','pension']:
            market_defacto[agent+'_possession'] = market_defacto[agent].cumsum() + abs(min(market_defacto[agent].cumsum()))
        market_defacto['total_stock_in_circulation'] = market_defacto['individual_possession'] + market_defacto['foreign_retail_possession'] + market_defacto['institution_possession'] + market_defacto['etc_corporate_possession']

        # remove zero in each agent_possession
        for agent in ['individual','foreign_retail','institution','etc_corporate','trust','pension']:
            market_defacto[agent+'_possession'] = [1 if x==0 else x for x in market_defacto[agent+'_possession']]
        market_defacto['total_stock_in_circulation'] = [1 if x==0 else x for x in market_defacto['total_stock_in_circulation']]

    def agent_height(self, ticker):
        # calculate height
        for agent in ['individual','foreign_retail','institution','etc_corporate']:
            market_defacto[agent+'_height'] = round(market_defacto[agent+'_possession']/market_defacto['total_stock_in_circulation'],3)
        market_defacto['institution_purity'] = round((market_defacto['trust_possession'] + market_defacto['pension_possession'])/market_defacto['total_stock_in_circulation'],3)

        # calculate proportion
        for agent in ['individual','foreign_retail','institution','etc_corporate']:
            market_defacto[agent+'_proportion'] = round(market_defacto[agent+'_buy']/market_defacto['volume'],3)

    def agent_true_price(self, ticker):
        for agent in ['individual','foreign_retail','institution','etc_corporate']:
            market_defacto[agent + '_tp'] = 0
            market_defacto.loc[(market_defacto[agent] > 0) & (market_defacto['close_price'] > market_defacto['open_price']), agent + '_tp'] = (market_defacto[agent+'_height']*(((3*market_defacto['low_price'])+market_defacto['high_price'])/4))+((1-market_defacto[agent+'_height'])*(((3*market_defacto['high_price'])+market_defacto['low_price'])/4))
            market_defacto.loc[(market_defacto[agent] > 0) & (market_defacto['close_price'] == market_defacto['open_price']), agent + '_tp'] = (market_defacto['high_price']+market_defacto['low_price'])/2
            market_defacto.loc[(market_defacto[agent] > 0) & (market_defacto['close_price'] < market_defacto['open_price']), agent + '_tp'] = (market_defacto[agent+'_height']*(((3*market_defacto['low_price'])+market_defacto['high_price'])/4))+((1-market_defacto[agent+'_height'])*(((3*market_defacto['high_price'])+market_defacto['low_price'])/4))

            market_defacto.loc[(market_defacto[agent] == 0) & (market_defacto['close_price'] > market_defacto['open_price']), agent + '_tp'] = (market_defacto['high_price']+market_defacto['low_price'])/2
            market_defacto.loc[(market_defacto[agent] == 0) & (market_defacto['close_price'] == market_defacto['open_price']), agent + '_tp'] = (market_defacto['high_price']+market_defacto['low_price'])/2
            market_defacto.loc[(market_defacto[agent] == 0) & (market_defacto['close_price'] < market_defacto['open_price']), agent + '_tp'] = (market_defacto['high_price']+market_defacto['low_price'])/2

            market_defacto.loc[(market_defacto[agent] < 0) & (market_defacto['close_price'] > market_defacto['open_price']), agent + '_tp'] = (market_defacto[agent+'_height']*(((3*market_defacto['high_price'])+market_defacto['low_price'])/4))+((1-market_defacto[agent+'_height'])*(((3*market_defacto['low_price'])+market_defacto['high_price'])/4))
            market_defacto.loc[(market_defacto[agent] < 0) & (market_defacto['close_price'] == market_defacto['open_price']), agent + '_tp'] = (market_defacto['high_price']+market_defacto['low_price'])/2
            market_defacto.loc[(market_defacto[agent] < 0) & (market_defacto['close_price'] < market_defacto['open_price']), agent + '_tp'] = (market_defacto[agent+'_height']*(((3*market_defacto['high_price'])+market_defacto['low_price'])/4))+((1-market_defacto[agent+'_height'])*(((3*market_defacto['low_price'])+market_defacto['high_price'])/4))

    def agent_average_price_per_share(self, ticker):
        pass


class ScannerProcessor:

    # *** UPDATE: 20180824 ***#
    def __init__(self, taskname, today_date=None):
        self.taskname = taskname.lower()
        if today_date == None:
            self.today_date = timezone.now().strftime('%Y%m%d')
        else:
            self.today_date = today_date
        self.data = Data('scanner')

    # *** UPDATE: 20180824 ***#
    def reduce(self):
        taskname = self.taskname
        if hasattr(self, taskname):
            reducer = getattr(self, taskname)
            response = reducer()
            return response
        else:
            return {'state': '{} 태스크는 없습니다'.format(taskname)}

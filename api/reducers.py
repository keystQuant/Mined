import datetime
import pandas as pd

from .models import (
    Date,
    Ticker,
    StockInfo,
    Index,
    ETF,
    OHLCV,
    BuySell,
    MarketCapital,
    Factor,
)
from .cache import RedisClient

from algorithms.data import DATA_MAPPER, MARKET_CODES, Data

from mined.settings import RAVEN_CONFIG
from raven import Client
client = Client(RAVEN_CONFIG['dsn'])


class Reducers:

    def __init__(self, action_type, env_type):
        # action_type should be a str
        self.ACTION = action_type.lower()

        self.ENV = env_type.lower() # this is so you can run Node crawler app (Gobble) from local env
        # set ENV to local if you with to run on a local machine

        # define cache
        self.redis = RedisClient()

    def has_reducer(self):
        # return True if reducer is defined, else False
        if hasattr(self, self.ACTION):
            return True
        else:
            return False

    def reduce(self):
        try:
            reducer = getattr(self, self.ACTION)
            # run reducer
            reducer() # pass in ENV to run locally if told to
        except:
            client.captureException()
            return False # return False on error

        # return True when function ran properly
        return True

    ##### Preprocessing Process #####
    def preprocess_data(self):
        ##### 데이터 분석에 필요한 데이터를 한번에 정리하여 preprocessing한다
        ##### 코스피, 코스닥 따로 생성

        data = Data('rms')

        # 1. OHLCV 데이터에서 cls_prc만 모으기
        kospi_cls = data._add_all_stocks_in_one_df(data.kospi_tickers, 'ohlcv', 'cls_prc')
        kosdaq_cls = data._add_all_stocks_in_one_df(data.kosdaq_tickers, 'ohlcv', 'cls_prc')

        if self.redis.key_exists('KOSPI_CLS_PRC')
            self.redis.del_key('KOSPI_CLS_PRC')
        if self.redis.key_exists('KOSDAQ_CLS_PRC')
            self.redis.del_key('KOSDAQ_CLS_PRC')

        self.redis.set_df('KOSPI_CLS_PRC', kospi_cls)
        self.redis.set_df('KOSDAQ_CLS_PRC', kosdaq_cls)

        # 2. OHLCV 데이터에서 adj_prc만 모으기
        # 3. OHLCV 데이터에 trd_qty만 모으기
        data.request('close')

        if self.redis.key_exists('KOSPI_OHLCV'):
            self.redis.del_key('KOSPI_OHLCV')
        if self.redis.key_exists('KOSPI_VOL')
            self.redis.del_key('KOSPI_VOL')

        if self.redis.key_exists('KOSDAQ_OHLCV'):
            self.redis.del_key('KOSDAQ_OHLCV')
        if self.redis.key_exists('KOSDAQ_VOL')
            self.redis.del_key('KOSDAQ_VOL')

        self.redis.set_df('KOSPI_OHLCV', data.kospi_cls_df)
        self.redis.set_df('KOSPI_VOL', data.kospi_vol_df)
        self.redis.set_df('KOSDAQ_OHLCV', data.kosdaq_cls_df)
        self.redis.set_df('KOSDAQ_VOL', data.kosdaq_vol_df)

        # 4. adj_prc * trd_qty해서 거래대금 만들기
        kospi_prc_vol = kospi_cls * data.kospi_vol_df
        kosdaq_prc_vol = kosdaq_cls * data.kosdaq_vol_df

        if self.redis.key_exists('KOSPI_PRC_VOL')
            self.redis.del_key('KOSPI_PRC_VOL')
        if self.redis.key_exists('KOSDAQ_PRC_VOL')
            self.redis.del_key('KOSDAQ_PRC_VOL')

        self.redis.set_df('KOSPI_PRC_VOL', kospi_prc_vol)
        self.redis.set_df('KOSDAQ_PRC_VOL', kosdaq_prc_vol)

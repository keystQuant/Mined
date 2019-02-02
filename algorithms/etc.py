import time, datetime
import pandas as pd

from api.cache import RedisClient


KOSPI_TICKERS = 'KOSPI_TICKERS'
KOSDAQ_TICKERS = 'KOSDAQ_TICKERS'
ETF_TICKERS = 'ETF_TICKERS'
ETF_FULL_TICKERS = 'ETF_FULL_TICKERS'
ETN_TICKERS = 'ETN_TICKER'

MKT_DF_KEY = "MKTCAP_DF"
PRI_DF_KEY = "PRI_SELL_DF"
FRG_DF_KEY = "FRG_NET_DF"
INS_DF_KEY = "INS_NET_DF"

KOSPI_OHLCV = 'KOSPI_OHLCV'
KOSDAQ_OHLCV = 'KOSDAQ_OHLCV'
ETF_OHLCV = 'ETF_OHLCV'


class KeystETCAlgorithm:

    def __init__(self):
        self.redis = RedisClient()
        self.pri_df = self.redis.get_df(PRI_DF_KEY)
        self.frg_df = self.redis.get_df(FRG_DF_KEY)
        self.ins_df = self.redis.get_df(INS_DF_KEY)
        self.mkt_cap_df = self.redis.get_df(MKT_DF_KEY)
        self.kp_tickers = [ticker.decode() for ticker in self.redis.redis_client.lrange(KOSPI_TICKERS, 0 ,-1)]
        self.kd_tickers = [ticker.decode() for ticker in self.redis.redis_client.lrange(KOSDAQ_TICKERS, 0 ,-1)]
        self.total_tickers = self.kd_tickers + self.kp_tickers
        self.except_tickers = self.redis.get_list(ETF_FULL_TICKERS) + self.redis.get_list(ETN_TICKERS)
        self.kp_ohlcv = self.redis.get_df(KOSPI_OHLCV)
        self.kd_ohlcv = self.redis.get_df(KOSDAQ_OHLCV)
        self.etf_ohlcv = self.redis.get_df(ETF_OHLCV)
        self.except_ticker = self.redis.get_list(ETF_FULL_TICKERS) + self.redis.get_list(ETN_TICKERS)
        self.total_ohlcv = pd.concat([self.kp_ohlcv, self.kd_ohlcv, self.etf_ohlcv], axis=1)
        print("algoritms start")

    def make_ticker_dict(self):
        total_tickers_dict = dict()
        for ticker in self.total_tickers:
            total_tickers_dict[ticker.split('|')[0]] = ticker.split('|')[1]
        return total_tickers_dict

    def mkt_cap_calc(self, mkt_cap_df, pri_df):
        start = time.time()
        global total_mkt_cap
        ticker_list = self.pri_df.columns.tolist()
        refined_tickers = [t for t in ticker_list if t not in self.except_tickers]
        make_data_start = False
        i = 0
        for ticker in refined_tickers:
            i+=1
            if i % 100==0:
                print(i,':',ticker)
            mkt_df = mkt_cap_df[[ticker]]*self.total_ohlcv[[ticker]]
            if make_data_start == False:
                total_mkt_cap = mkt_df
                make_data_start = True
            else:
                total_mkt_cap = pd.concat([total_mkt_cap, mkt_df], axis=1)
        print("all process is done!")
        end = time.time()
        print(end-start)
        return total_mkt_cap

    def mkt_cap_buysell(self, mode):
        start = time.time()
        total_mkt_cap = self.mkt_cap_calc(self.mkt_cap_df, self.pri_df)
        global total_rank_df
        if mode == 'pri':
            analysis_df = self.pri_df
        elif mode == 'frg':
            analysis_df = self.frg_df
        elif mode == 'ins':
            analysis_df = self.ins_df
        else:
            print("Error")
        ticker_list = analysis_df.columns.tolist()
        make_data_start = False
        i = 0
        for ticker in ticker_list:
            i+=1
            if i % 100==0:
                print(i,':',ticker)
            mkt_divide = analysis_df[[ticker]]/total_mkt_cap[[ticker]]
            temp_rank = mkt_divide.rank(method='min')
            if make_data_start == False:
                total_rank_df = temp_rank
                make_data_start = True
            else:
                total_rank_df = pd.concat([total_rank_df, temp_rank], axis=1)
        print("all process is done!")
        end = time.time()
        print(end-start)
        return total_rank_df

    def make_cache_data(self, mode):
        ticker_dict = self.make_ticker_dict()
        if mode == 'pri':
            rank_df = self.mkt_cap_buysell('pri')
            col_name = "{} sell rank".format(mode)
        elif mode == 'frg':
            rank_df = self.mkt_cap_buysell('frg')
            col_name = "{} net rank".format(mode)
        elif mode == 'ins':
            rank_df = self.mkt_cap_buysell('ins')
            col_name = "{} net rank".format(mode)
        else:
            print("error")
        recent_date = rank_df.tail(1).index.tolist()[0].strftime('%Y%m%d')
        print(recent_date, col_name)
        ticker_df = pd.DataFrame.from_dict(ticker_dict, orient='index')
        ticker_df.columns = ['name']
        ticker_df['code'] = ticker_df.index
        recent_mkt= total_mkt_cap.tail(1).T
        recent_mkt.columns = ['mkt_cap']
        recent_mkt['code'] = recent_mkt.index
        recent_rank = rank_df.tail(1).T
        recent_rank.columns = [col_name]
        recent_rank['code'] = recent_rank.index
        cache_df = pd.merge(pd.merge(recent_rank, ticker_df, on='code', how='inner'),recent_mkt, on='code', how='inner')
        cache_df = cache_df.sort_values(col_name)
        cache_df.dropna(inplace=True)
        return cache_df

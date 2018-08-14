'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import math, time
from datetime import datetime
import numpy as np
from numpy import *
import pandas as pd
import scipy.optimize

from algorithms.data import Data


class RMS:
    """
    RMS: Risk Management System

    ** 설명:

    ** 태스크:
    1.
    """

    #*** UPDATE: 20180815 ***#
    def __init__(self, mode='score', ratio_dict=None):
        # 인자 설명:

        ### mode (str) --> RMS을 포트폴리오 분석용, 최적 포트폴리오 계산용, 점수 계산용으로 사용할 수 있다
        ###                portfolio, recommendation, score: 세 가지 옵션을 줄 수 있다
        ### ratio_dict (dict) --> algorithms.portfolio.PortfolioProcessor가 redistribute하고
        ###                       최종적으로 생기는 ratio_dict와 같은 형식
        self.ratio_dict = ratio_dict

        # RMS 계산에는 종가 데이터만 있으면 된다!! #
        # Data 인스턴스는 종가만 모아서 리턴할 수 있도록 한다

        # 새팅 딕셔너리를 준비한다
        # --> ratio_dict의 키를 사용해서 ticker_list를 채우고,
        #     Data 인스턴스로 그 주식들의 종가 데이터를 불러올 것이다
        self.settings = {
            'ticker_list': list(),
            'ohlcv_list': list()
        }

    #*** UPDATE: 20180815 ***#
    def set_port_analysis_settings(self):
        ### 포트폴리오 분석, 최적 포트폴리오 계산용 옵션이다
        ### mode == 'portfolio' or mode == 'recommendation'

        # ticker_list 리스트 채우기
        self.settings['ticker_list'] = [ticker for ticker in self.ratio_dict.keys() if ticker != 'cash']
        ticker_list = self.settings['ticker_list']

        # Data 인스턴스 생성
        self.data = Data('rms', ticker_list) # Data 인스턴스 생성자 stocks 인자를 넣어준다

        # ohlcv_list 리스트 생성하기
        print('create ohlcv_list with Data instance')

    #*** UPDATE: 20180815 ***#
    def set_periodic_close(self, ohlcv_df, period='M'):
        ### 인자 설명:
        ### 1. ohlcv_df (pd.DataFrame)
        ### 2. period (str) --> W, M, Q, 6M, A
        ###                     일주일, 한달, 세달, 여섯달, 일년 주기 종가

        # 인자로 받은 데이터프레임 ohlcv_df의 인덱스를 데이트타임으로 바꿔준다
        ohlcv_df.index = pd.to_datetime(ohlcv_df.index)
        periodic_close = ohlcv_df.resample(period).last() # reference: http://benalexkeen.com/resampling-time-series-data-with-pandas/

        ##########################################
        ##### 6개월 resample은 따로 처리 필요!!! ######
        ##########################################
        # --> 우선은 1달을 주기로 계산하는 공식이 많기 때문에 추후에 추가해도됨

        periodic_close.dropna(how='all', inplace=True)
        return periodic_close


    ##### EAA (Elastic Asset Allocation) 알고리즘에 필요한 계산 #####


    #*** UPDATE: 20180815 ***#
    def dual_momentum(self, data):
        # data (pd.DataFrame) --> 한 달을 주기로 resample된 데이터프레임
        # resample 처리가 안 된 상태라면, set_periodic_close() 메소드 사용
        for i in range(1, 13):
            momentum = (data - data.shift(i))/data.shift(i) # 단순 수익률: (P(t) - P(t-i))/P(t-i), P = 종가
            if i == 1:
                temp = momentum
            else:
                temp += momentum
        mom = temp/12 # 위에서 구한 모든 모멘텀값을 더한 후 12로 나눔 (12개월 평균 모멘텀이 된다)
        return mom.fillna(0) # nan은 0으로 처리

    def volatility(self):





class PortfolioAlgorithm:
    '''

    **설명:

    **태스크:
    1.

    '''

    #*** UPDATE: 20180725 ***#
    def __init__(self, taskname, ratio_dict, filter_date=False):
        self.taskname = taskname

        self.ratio_dict = ratio_dict
        recent_update_date = BM.objects.filter(name='KOSPI').order_by('-date').first().date
        year = recent_update_date[:4]
        month = recent_update_date[4:6]
        if not filter_date:
            last_year = str(int(year) - 5)
            last_month = int(month) - 1 or 12
            last_month = str(last_month).zfill(2)
            filter_date = last_year + last_month + '00'
            self.filter_date = filter_date
        else:
            self.filter_date = filter_date
        self.ohlcv_df = pd.DataFrame()
        self.settings = {
            'ticker_list': list(),
            'ohlcv_list': list()
        }
        self._start_df_setup() # fill in ticker_list and ohlcv_list
        self._retrieve_weights()
        self._create_ohlcv_df()
        self._calc_port_returns()

    def _start_df_setup(self):
        # setting ticker_list
        self.settings['ticker_list'] = [ticker for ticker in self.ratio_dict.keys() if ticker != 'cash']
        ticker_list = self.settings['ticker_list']
        # setting ohlcv_list
        init_qs = OHLCV.objects.filter(code__in=ticker_list)
        filtered_qs = init_qs.exclude(date__lte=self.filter_date).order_by('date')
        ohlcv_qs = filtered_qs.values_list('code', 'date', 'close_price')
        ohlcv_list = []
        for ticker in ticker_list:
            ticker_ohlcv = [{'date': data[1], 'close_price': data[2]} for data in ohlcv_qs if data[0] == ticker]
            ohlcv_list.append(ticker_ohlcv)
        self.settings['ohlcv_list'] = ohlcv_list

    def _retrieve_weights(self):
        S = list()
        W = list()
        for key, val in self.ratio_dict.items():
            if key != 'cash':
                S.append(key)
                W.append(val['ratio'])
        W = pd.Series(W, index=S)
        self.W = W

    def _create_ohlcv_df(self):
        ticker_count = len(self.settings['ticker_list'])
        if ticker_count == 0:
            pass
        elif ticker_count == 1:
            ticker = self.settings['ticker_list'][0]
            ohlcv = self.settings['ohlcv_list'][0]
            self.ohlcv_df = self._create_df(ticker, ohlcv)
        else:
            for i in range(ticker_count):
                ticker = self.settings['ticker_list'][i]
                ohlcv = self.settings['ohlcv_list'][i]
                if i == 0:
                    df = self._create_df(ticker, ohlcv)
                else:
                    temp_df = self._create_df(ticker, ohlcv)
                    df = pd.concat([df, temp_df], axis=1)
            df.index = pd.to_datetime(df.index)
            self.ohlcv_df = df

    def _create_df(self, ticker, ohlcv):
        df = pd.DataFrame(ohlcv)
        df.set_index('date', inplace=True)
        df.rename(columns={'close_price': ticker}, inplace=True)
        return df

    def _calc_port_returns(self, period='M'):
        # 현재 한 달 수익률만 계산한다
        # 추가할 사항: 3개월, 6개월, 1년 수익률 (각 기간별 종목 데이터가 없어서 계산이 안 된다면 0%)
        self.ohlcv_df.index = pd.to_datetime(self.ohlcv_df.index)
        R = self.ohlcv_df.resample(period).last().pct_change()
        R.dropna(how='all', inplace=True)
        self.R = R

    def portfolio_info(self):
        BM_wr, BM_r, BM_v, BM_yc = self._bm_specs()
        wr, r, v, yc = self._backtest_port(self.W, self.R)
        sr = self._sharpe_ratio(r, BM_r, v)
        yield_r = yc.ix[len(yc)-1] - 1
        bt = pd.concat([yc, BM_yc], axis=1)
        bt.columns = ['Portfolio', 'Benchmark']
        return r, v, sr, yield_r, bt

    def _bm_specs(self, period='M'):
        from stockapi.models import BM
        BM_qs = BM.objects.filter(name='KOSPI').distinct('date')
        BM_data = list(BM_qs.exclude(date__lte=self.filter_date).values('date', 'index'))
        BM = pd.DataFrame(BM_data)
        BM.set_index('date', inplace=True)
        BM.index = pd.to_datetime(BM.index)
        BM.rename(columns={'index': 'Benchmark'}, inplace=True)
        BM_R = BM.resample(period).last().pct_change()
        BM_R.dropna(how='all', inplace=True)
        W = pd.Series([1], index=['Benchmark'])
        return self._backtest_port(W, BM_R)

    def _backtest_port(self, W=None, BM=None):
        if type(W) == type(None) and type(BM) == type(None):
            W_R = self.W * self.R
        else:
            W_R = W*BM
        WR = W_R.sum(axis=1)
        port_ret = WR.mean()
        port_var = WR.std()
        yield_curve = (WR + 1).cumprod()
        return WR, port_ret, port_var, yield_curve

    def _sharpe_ratio(self, r, bm_r, v):
        return (r - bm_r)/v

    def change_bt_format(self, bt):
        new_data = dict()
        for column in bt.columns:
            ret_data = list()
            dates = bt.index.astype(np.int64)//1000000 # pandas timestamp returns in microseconds, divide by million
            for i in range(len(bt)):
                data = bt.ix[i]
                date = dates[i]
                ret_data.append([date, float(format(round(data[column], 4), '.4f'))])
            new_data[column] = ret_data
        return new_data


class EAA(PortfolioAlgorithm):
    # def add_bm_data(self):
    #     BM_qs = OHLCV.objects.filter(code='BM')
    #     BM_data = list(BM_qs.exclude(date__lte=self.filter_date).values('date', 'close_price'))
    #     BM = pd.DataFrame(BM_data)
    #     BM.set_index('date', inplace=True)
    #     BM.index = pd.to_datetime(BM.index)
    #     BM.rename(columns={'close_price': 'Benchmark'}, inplace=True)
    #     BM = BM.resample('M').last().pct_change()
    #     self.R.index = pd.to_datetime(self.R.index)
    #     self.R = pd.concat([self.R, BM], axis=1)
    #     self.R.fillna(0, inplace=True)

    def _set_monthly_close(self, period='M'):
        self.ohlcv_df.index = pd.to_datetime(self.ohlcv_df.index)
        monthly_close = self.ohlcv_df.resample(period).last()
        monthly_close.dropna(how='all', inplace=True)
        self.monthly_close = monthly_close

    def _dual_momentum(self):
        monthly_close = self.monthly_close
        for i in range(1, 13):
            momentum = (monthly_close - monthly_close.shift(i))/monthly_close.shift(i)
            if i == 1:
                temp = momentum
            else:
                temp += momentum
        mom = temp/12
        # return mom.ix[-1]
        return mom.fillna(0)

    def _volatility(self):
        # return self.R.rolling(window=12).std().ix[-1]
        return self.R.rolling(window=12).std().fillna(0)

    def _correlation(self):
        corr = self.R.copy()
        corr['Eq_weight'] = list(pd.DataFrame(corr.values.T*(1.0/len(corr.columns))).sum())
        return corr.corr().ix[-1][:-1]

    def EAA(self, mom, vol, corr):
        cash_amount = (len(mom) - len(mom[mom > 0]))/len(mom)
        stock_amount = 1 - cash_amount
        eaa_amount = (1 - corr[mom > 0])/vol[mom > 0]
        stock_amount = stock_amount*eaa_amount/eaa_amount.sum()
        return cash_amount, stock_amount

    def backtest_EAA(self):
        self._set_monthly_close()
        mom = self._dual_momentum()
        vol = self._volatility()
        corr = self._correlation()
        returns_list = []
        for date in range(len(self.R)):
            cash_amt, stock_amt = self.EAA(mom.ix[date], vol.ix[date], corr)
            returns = ( self.R.ix[date] * (stock_amt * (1 - cash_amt)) ).fillna(0)
            returns_list.append(returns.sum())
        weights = []
        for ticker in self.settings['ticker_list']:
            wt_df = stock_amt * (1 - cash_amt)
            try:
                weight = wt_df[ticker]
            except KeyError:
                weight = 0
            weights.append(float(format(round(weight, 4), '.4f')))
        wr = pd.DataFrame(returns_list)
        r = wr.mean()[0]
        v = wr.std()[0]
        yc = (wr + 1).cumprod()
        BM_wr, BM_r, BM_v, BM_yc = self._bm_specs()
        sr = self._sharpe_ratio(r, BM_r, v)
        yield_r = (yc.ix[len(yc) - 1] - 1)[0]
        yc.index = BM_yc.index
        bt = pd.concat([yc, BM_yc], axis=1)
        bt.columns = ['Portfolio', 'Benchmark']
        return r, v, sr, yield_r, bt, weights


class StockScorer:
    def __init__(self, taskname):
        self.taskname = taskname

        self.data = Data('rms')

    def score_data(self):
        self.vol = (self.data.ohlcv_df * self.data.vol_df).ix[-1]
        self.set_return_portfolio()
        self.add_bm_data()
        self.make_mom_volt_cor_vol()

    def set_return_portfolio(self):
        self.portfolio_data = self.data.ohlcv_df.pct_change()

    def add_bm_data(self):
        # 캐시에서 데이터를 들고온 후에 코스피 인덱스의 날짜와 종가를 전체 종가 데이터에 붙여준다
        BM_qs = OHLCV.objects.filter(code='BM')
        BM_data = list(BM_qs.exclude(date__lte=self.filter_date).values('date', 'close_price'))
        BM = pd.DataFrame(BM_data)
        BM.set_index('date', inplace=True)
        BM.index = pd.to_datetime(BM.index)
        BM.rename(columns={'close_price': 'Benchmark'}, inplace=True)
        BM = BM.pct_change()
        self.portfolio_data.index = pd.to_datetime(self.portfolio_data.index)
        self.portfolio_data = pd.concat([self.portfolio_data, BM], axis=1)
        self.portfolio_data.fillna(0, inplace=True)

    def make_mom_volt_cor_vol(self, period='M'):
        # period는 점수를 내는 주기로 1달 3달 6달 1년을 계산한다
        eaa = EAA(period)

'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import numpy as np
import pandas as pd

from algorithms.data import Data
from algorithms.utils import correlation, dual_momentum, score, volatility


class RMSProcessor:

    # *** UPDATE: 20180915 ***#
    def __init__(self, taskname, ratio_dict=None):
        self.taskname = taskname.lower()

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

        self.set_port_analysis_settings()

    # *** UPDATE: 20180824 ***#
    def reduce(self):
        taskname = self.taskname
        if hasattr(self, taskname):
            reducer = getattr(self, taskname)
            response = reducer()
            return response
        else:
            return {'state': '{} 태스크는 없습니다'.format(taskname)}

    # *** UPDATE: 20180915 ***#
    def set_port_analysis_settings(self):
        if self.ratio_dict:
            self.settings['ticker_list'] = [ticker for ticker in self.ratio_dict.keys() if ticker != 'cash']

        self.data = Data('rms', self.settings['ticker_list'])

        # ohlcv_list 리스트 생성하기
        print('create ohlcv_list with Data instance')

    # *** UPDATE: 20180815 ***#
    def set_periodic_close(self, ohlcv_df, period='M'):
        ### 인자 설명:
        ### 1. ohlcv_df (pd.DataFrame)
        ### 2. period (str) --> W, M, Q, 6M, A
        ###                     일주일, 한달, 세달, 여섯달, 일년 주기 종가

        # 인자로 받은 데이터프레임 ohlcv_df의 인덱스를 데이트타임으로 바꿔준다
        ohlcv_df.index = pd.to_datetime(ohlcv_df.index)
        periodic_close = ohlcv_df.resample(
            period).last()  # reference: http://benalexkeen.com/resampling-time-series-data-with-pandas/

        ##########################################
        ##### 6개월 resample은 따로 처리 필요!!! ######
        ##########################################
        # --> 우선은 1달을 주기로 계산하는 공식이 많기 때문에 추후에 추가해도됨

        periodic_close.dropna(how='all', inplace=True)
        return periodic_close

    ##### EAA (Elastic Asset Allocation) 알고리즘에 필요한 계산 #####

    # *** UPDATE: 20180816 ***#
    def EAA(self, mom, vol, corr, portfolio_type=''):
        # 1단계: 현금 투자 금액을 계산한다
        if portfolio_type == 'S':
            cash_amount = 0
            stock_amount = 1
        else:
            # 투자하는 종목 중에서 모멘텀이 양수인 종목/자산군에만 투자한다
            cash_amount = (len(mom) - len(mom[mom > 0])) / len(mom)
            stock_amount = 1 - cash_amount
        # 2단계: (1 - 상관관계) / 변동성 의 공식으로 주식에 투자해야하는 금액을 계산한다
        eaa_amount = (1 - corr[mom > 0]) / vol[mom > 0]
        # 3단계: 주식에 투자해야하는 금액을 리스트 형식으로 바꾼다
        # --> 각 종목/자산군에 투자해야하는 금액이다
        stock_amount = stock_amount * eaa_amount / eaa_amount.sum()
        return cash_amount, stock_amount

    ##### 알고리즘 백테스팅(backtesting)에 필요한 계산 #####

    # *** UPDATE: 20180816 ***#
    def calc_port_returns(self, ohlcv_df):
        # OHLCV 데이터를 받아서 수익률 데이터로 변환해준다
        return ohlcv_df.pct_change()

    # *** UPDATE: 20180816 ***#
    def retrieve_weights(self, ratio_dict):
        stocks = list()
        weights = list()
        for code, ratio in ratio_dict.items():
            if code != 'cash':
                stocks.append(code)
                weights.append(ratio['ratio'])
        weights = pd.Series(weights, index=stocks)
        return weights

    # *** UPDATE: 20180816 ***#
    def backtest_portfolio(self, weights, returns):
        W_R = weights * returns
        WR = W_R.sum(axis=1)
        port_ret = WR.mean()
        port_var = WR.std()
        yield_curve = (WR + 1).cumprod()
        return WR, port_ret, port_var, yield_curve

    # *** UPDATE: 20180915 ***#
    def benchmark_info(self):
        ms_data = Data('marketsignal')
        ms_data.request('bm')
        benchmark = ms_data.kospi_index
        benchmark_cls = benchmark[['date', 'cls_prc']]
        benchmark_cls.set_index('date', inplace=True)
        benchmark_cls.index = pd.to_datetime(benchmark_cls.index)
        benchmark_cls.rename(columns={'cls_prc': 'Benchmark'}, inplace=True)
        BM_R = benchmark_cls.resample('M').last().pct_change()
        BM_R.dropna(how='all', inplace=True)
        W = pd.Series([1], index=['Benchmark'])
        return self.backtest_portfolio(W, BM_R)

    # *** UPDATE: 20180816 ***#
    def portfolio_info(self, weights, returns):
        ### BM_wr: Benchmark Weight * Return
        ### BM_r: Benchmark Return
        ### BM_v: Benchmark Volatility
        ### BM_yc: Benchmark Yield Curve
        BM_wr, BM_r, BM_v, BM_yc = self.benchmark_info()
        wr, r, v, yc = self.backtest_portfolio(weights, returns)

        sharpe_ratio = self.sharpe_ratio(r, BM_r, v)
        yield_r = yc.ix[len(yc) - 1] - 1
        bt = pd.concat([yc, BM_yc], axis=1)
        bt.columns = ['Portfolio', 'Benchmark']
        return r, v, sharpe_ratio, yield_r, bt

    # *** UPDATE: 20180816 ***#
    def sharpe_ratio(self, r, bm_r, v):
        return (r - bm_r) / v

    # *** UPDATE: 20180915 ***#
    def backtest_eaa(self):
        data = self.data
        data.request('close')

        cls_df = pd.concat([data.kospi_cls_df, data.kosdaq_cls_df], axis=1, sort=True)
        base = self.set_periodic_close(cls_df, period='M')

        mom = dual_momentum(base)
        vol = volatility(base, window=12)
        corr = correlation(base, window=12)

        returns_list = []
        for index, row in cls_df.iterrows():
            cash_amt, stock_amt = self.EAA(mom.ix[index], vol.ix[index], corr)
            returns = (row * (stock_amt * (1 - cash_amt))).fillna(0)
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
        BM_wr, BM_r, BM_v, BM_yc = self.benchmark_info()
        sr = self.sharpe_ratio(r, BM_r, v)
        yield_r = (yc.ix[len(yc) - 1] - 1)[0]
        yc.index = BM_yc.index
        bt = pd.concat([yc, BM_yc], axis=1)
        bt.columns = ['Portfolio', 'Benchmark']
        return r, v, sr, yield_r, bt, weights

    # *** UPDATE: 20180816 ***#
    def change_backtest_result_format(self, backtest_result):
        new_data = dict()
        for column in bt.columns:
            ret_data = list()
            dates = bt.index.astype(np.int64) // 1000000  # pandas timestamp returns in microseconds, divide by million
            for i in range(len(bt)):
                data = bt.ix[i]
                date = dates[i]
                ret_data.append([date, float(format(round(data[column], 4), '.4f'))])
            new_data[column] = ret_data
        return new_data

    ##### 종목 점수 매기는데 필요한 계산 #####

    # *** UPDATE: 20180915 ***#
    def score_data(self):
        data = self.data
        data.request('close')

        kp_total_score = score(data.kospi_cls_df, data.kospi_vol_df, include_correlation=False)
        kd_total_score = score(data.kosdaq_cls_df, data.kosdaq_vol_df, include_correlation=False)

        return kp_total_score, kd_total_score

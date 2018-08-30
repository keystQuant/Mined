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


class RMSProcessor:

    # *** UPDATE: 20180824 ***#
    def __init__(self, taskname, ratio_dict=None):
        self.taskname = taskname.lower()
        self.data = Data('rms')

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

    # *** UPDATE: 20180824 ***#
    def reduce(self):
        taskname = self.taskname
        if hasattr(self, taskname):
            reducer = getattr(self, taskname)
            response = reducer()
            return response
        else:
            return {'state': '{} 태스크는 없습니다'.format(taskname)}

    # *** UPDATE: 20180815 ***#
    def set_port_analysis_settings(self):
        ### 포트폴리오 분석, 최적 포트폴리오 계산용 옵션이다
        ### mode == 'portfolio' or mode == 'recommendation'

        # ticker_list 리스트 채우기
        self.settings['ticker_list'] = [ticker for ticker in self.ratio_dict.keys() if ticker != 'cash']
        ticker_list = self.settings['ticker_list']

        # Data 인스턴스 생성
        self.data = Data('rms', ticker_list)  # Data 인스턴스 생성자 stocks 인자를 넣어준다

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

    # *** UPDATE: 20180815 ***#
    def dual_momentum(self, data):
        # data (pd.DataFrame) --> 한 달을 주기로 resample된 데이터프레임
        # resample 처리가 안 된 상태라면, set_periodic_close() 메소드 사용
        for i in range(1, 13):
            momentum = (data - data.shift(i)) / data.shift(i)  # 단순 수익률: (P(t) - P(t-i))/P(t-i), P = 종가
            if i == 1:
                temp = momentum
            else:
                temp += momentum
        mom = temp / 12  # 위에서 구한 모든 모멘텀값을 더한 후 12로 나눔 (12개월 평균 모멘텀이 된다)
        return mom.fillna(0)  # nan은 0으로 처리

    # *** UPDATE: 20180815 ***#
    def volatility(self, returns_data, window=12):
        # 변동성 계산
        # 보통 변동성 계산은 일년을 주기로 계산한다
        # 그래서 returns_data 월별로 resample된거라면 window를 12로 잡는다
        # (데이터가 일일 데이터면 보통 window를 200으로 잡는다)
        # (데이터가 일주일로 resample되었다면, window는 48을 잡는다)
        # (3개월/분기별로 resample 되었다면 window는 4로 잡는다)
        return returns_data.rolling(window=window).std().fillna(0)

    # *** UPDATE: 20180816 ***#
    def correlation(self, returns_data, window=12):
        corr = returns_data.copy()  # data를 복사한다
        corr['Eq_weight'] = list(pd.DataFrame(corr.values.T * (1.0 / len(corr.columns))).sum())
        return corr.rolling(window=window).corr().ix[-1][:-1]

    # *** UPDATE: 20180816 ***#
    def EAA(self, mom, vol, corr, portfolio_type):
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

    # *** UPDATE: 20180816 ***#
    def benchmark_info(self):
        ms_data = Data('marketsignal')
        ms_data.request('bm')

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

    # *** UPDATE: 20180822 ***#
    def backtest_EAA(self):
        self._set_monthly_close()
        mom = self._dual_momentum()
        vol = self._volatility()
        corr = self._correlation()
        returns_list = []
        for date in range(len(self.R)):
            cash_amt, stock_amt = self.EAA(mom.ix[date], vol.ix[date], corr)
            returns = (self.R.ix[date] * (stock_amt * (1 - cash_amt))).fillna(0)
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

    # *** UPDATE: 20180822 ***#
    def score_data(self):
        data = self.data
        data.request('close')

        kospi_cls_df = data.kospi_cls_df
        kospi_vol_df = data.kospi_vol_df
        kosdaq_cls_df = data.kosdaq_cls_df
        kosdaq_vol_df = data.kosdaq_vol_df

        # 1 단계: 코스피, 코스닥을 나눠서 거래대금 df를 만든다 --> 거래대금: 종가 * 거래량
        # 거래대금 정보를 만드는 이유는 거래대금으로 어떤 종목이 가장 많이 거래되고 있는지 파악 가능하기 때문이다
        ### kp_vol_prc에서 vol_prc란: volume in price values를 뜻함
        kp_vol_prc = kospi_cls_df * kospi_vol_df
        kd_vol_prc = kosdaq_cls_df * kosdaq_vol_df

        # 2 단계: 종가 데이터를 수익률 데이터로 바꾼다 (수익률 = return = 변화율)
        kospi_ret = kospi_cls_df.pct_change()
        kosdaq_ret = kosdaq_cls_df.pct_change()

        # 3 단계: 벤치마크 데이터를 하나씩 추가한다 (보편적으로 사용되는 벤치마크로 코스피 지수를 사용)
        # 데이터를 쉽게 가져오기 위해서 marketsignal 데이터 객체를 사용한다
        ms_data = Data('marketsignal')
        ms_data.request('bm')
        benchmark = ms_data.kospi_index
        benchmark = benchmark[['date', 'cls_prc']]
        benchmark.set_index('date', inplace=True)
        benchmark.index = pd.to_datetime(benchmark.index)
        benchmark.rename(columns={'cls_prc': 'Benchmark'}, inplace=True)
        benchmark = benchmark.pct_change()
        kospi = pd.concat([kospi_ret, benchmark], axis=1, sort=True)
        kosdaq = pd.concat([kosdaq_ret, benchmark], axis=1, sort=True)
        kospi.fillna(0, inplace=True)
        kosdaq.fillna(0, inplace=True)

        # 4 단계: 거래대금, 모멘텀, 변동성, 상관관계 점수를 매긴다
        # 우선, 모멘텀을 계산한다
        kp_mom = self.dual_momentum(kospi)
        kd_mom = self.dual_momentum(kosdaq)

        # 다음, 변동성을 계산한다
        kp_volt = self.volatility(kospi, 200)  # resample이 안 된 상태이다
        kd_volt = self.volatility(kosdaq, 200)

        # # 마지막으로 벤치마크 대비 종목별 상관관계를 계산한다
        # kp_cor = self.correlation(kospi, 200)
        # kd_cor = self.correlation(kosdaq, 200)

        ### kp_vol_prc, kp_mom, kp_volt, kp_cor, etc. 의 랭킹을 매긴다
        ### 랭킹은: 그 날짜별 모든 종목의 랭킹이다
        ### vol_prc, mom은 숫자가 클수록 좋고,
        ### volt, cor은 작을수록 좋다
        ### 그리고 랭킹을 가지고 점수를 매긴다
        ### --> 점수는: (종목 랭킹 / 종목수) * 100 이다
        kp_vol_score = kp_vol_prc.rank(ascending=True)
        kp_vol_score = (kp_vol_score / kp_vol_score.max()) * 100
        kd_vol_score = kd_vol_prc.rank(ascending=True)
        kd_vol_score = (kd_vol_score / kd_vol_score.max()) * 100

        kp_mom_score = kp_mom.rank(ascending=True)
        kp_mom_score = (kp_mom_score / kp_mom_score.max()) * 100
        kd_mom_score = kd_mom.rank(ascending=True)
        kd_mom_score = (kd_mom_score / kd_mom_score.max()) * 100

        kp_volt_score = kp_volt.rank(ascending=False)
        kp_volt_score = (kp_volt_score / kp_volt_score.max()) * 100
        kd_volt_score = kd_volt.rank(ascending=True)
        kd_volt_score = (kd_volt_score / kd_volt_score.max()) * 100

        # kp_cor_score = kp_cor.rank(ascending=False)
        # kp_cor_score = (kp_cor_score / kp_cor_score.max()) * 100
        # kd_cor_score = kd_cor.rank(ascending=False)
        # kd_cor_score = (kd_cor_score / kd_cor_score.max()) * 100

        # 5 단계: 토탈 점수를 계산한다
        ### 토탈 점수는 심플하게: (거래대금 점수 + 모멘텀 점수 + 변동성 점수 + 상관관계 점수) / 4 로 계산한다
        # kp_total_score = (kp_vol_score + kp_mom_score + kp_volt_score + kp_cor_score) // 4
        # kd_total_score = (kd_vol_score + kd_mom_score + kd_volt_score + kd_cor_score) // 4
        kp_total_score = (kp_vol_score + kp_mom_score + kp_volt_score) // 3
        kd_total_score = (kd_vol_score + kd_mom_score + kd_volt_score) // 3

        # 계산한 토탈 점수 데이터 두 개를 리턴한다
        return kp_total_score, kd_total_score

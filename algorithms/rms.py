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


class PortfolioAlgorithm:
    '''

    **설명:

    **태스크:
    1.

    '''

    #*** UPDATE: 20180725 ***#
    def __init__(self, ratio_dict, filter_date=False):
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


class BlackLitterman(PortfolioAlgorithm):
    # Markowitz Mean-Variance Optimization
    def _port_mean(self, W, R):
        return sum(R * W)

    def _port_var(self, W, C):
        return dot(dot(W, C), W)

    def _port_mean_var(self, W, R, C):
        return self._port_mean(W, R), self._port_var(W, C)

    def _risk_free_return(self):
        _, BM_r, _, _ = self._bm_specs()
        return BM_r

    def _solve_weights(self, W, R, C, rf):
        def fitness(W, R, C, rf):
            mean, var = self._port_mean_var(W, R, C)
            util = (mean - rf)/sqrt(var) # Sharpe ratio
            return 1/util
        n = len(W)
        b_ = [(0.,1.) for i in range(n)]
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. })
        optimized = scipy.optimize.minimize(fitness, W, (R, C, rf),
                    method='SLSQP', constraints=c_, bounds=b_)
        if not optimized.success:
            raise BaseException(optimized.message)
        return optimized.x

    # Black Litterman Model
    def _implied_return(self, W, R, C, rf):
        mean, var = self._port_mean_var(W, R, C)
        risk_aversion = (mean - rf)/var
        return dot(dot(risk_aversion, C), W)

    def _dual_momentum(self):
        return_data = self.R
        for i in range(1, 13):
            momentum = return_data - return_data.shift(i)
            if i == 1:
                temp = momentum
            else:
                temp += momentum
        mom = temp/12
        return mom.ix[-1]

    def _set_views(self):
        mom_s = self._dual_momentum()
        ticker_num = len(mom_s.index)
        views = []
        for i in range(ticker_num):
            ticker_i = mom_s.index[i]
            for j in range(i+1, ticker_num):
                ticker_j = mom_s.index[j]
                diff = mom_s[ticker_i] - mom_s[ticker_j]
                if diff > 0:
                    sign = '>'
                else:
                    sign = '<'
                view = (ticker_i, sign, ticker_j, abs(diff))
                views.append(view)
        return views

    def _create_views_and_link_matrix(self, names, views):
        r, c = len(views), len(names)
        Q = [views[i][3] for i in range(r)]  # view matrix
        P = zeros([r, c])
        nameToIndex = dict()
        for i, n in enumerate(names):
            nameToIndex[n] = i
        for i, v in enumerate(views):
            name1, name2 = views[i][0], views[i][2]
            P[i, nameToIndex[name1]] = +1 if views[i][1] == '>' else -1
            P[i, nameToIndex[name2]] = -1 if views[i][1] == '>' else +1
        return array(Q), P

    def optimize(self):
        n = len(self.W)
        W = ones([n])/n
        R = self.R.mean()
        C = self.R.cov()
        rf = self._risk_free_return()
        Pi = self._implied_return(W, R, C, rf)
        views = self._set_views()
        Q, P = self._create_views_and_link_matrix(self.settings['ticker_list'], views)
        tau = 0.025
        inv = np.linalg.inv
        omega = dot(dot(dot(tau, P), C), transpose(P))
        sub_a = inv(dot(tau, C))
        sub_b = dot(dot(transpose(P), inv(omega)), P)
        sub_c = dot(inv(dot(tau, C)), Pi)
        sub_d = dot(dot(transpose(P), inv(omega)), Q)
        Pi_adj = dot(inv(sub_a + sub_b), (sub_c + sub_d))
        # weights = self._solve_weights(W, Pi_adj + rf, C, rf)
        weights = self._solve_weights(W, Pi + rf, C, rf)
        weights = [float(format(round(weight, 4), '.4f')) for weight in weights]
        return weights

    def new_portfolio_info(self, W):
        W = pd.Series(W, index=self.settings['ticker_list'])
        BM_wr, BM_r, BM_v, BM_yc = self._bm_specs()
        wr, r, v, yc = self._backtest_port(W, self.R)
        sr = self._sharpe_ratio(r, BM_r, v)
        yield_r = yc.ix[len(yc)-1] - 1
        bt = pd.concat([yc, BM_yc], axis=1)
        bt.columns = ['Portfolio', 'Benchmark']
        return r, v, sr, yield_r, bt

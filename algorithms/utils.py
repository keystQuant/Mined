import time

import pandas as pd


def timeit(method):
    """decorator for timing processes"""

    def timed(*args, **kwargs):
        ts = time.time()
        method(*args, **kwargs)
        te = time.time()
        print("Process took " + str(te - ts) + " seconds")

    return timed


# *** UPDATE: 20180815 ***#
def dual_momentum(data):
    # data (pd.DataFrame) --> 한 달을 주기로 resample된 데이터프레임
    # resample 처리가 안 된 상태라면, set_periodic_close() 메소드 사용
    for i in range(1, 13):
        momentum = (data - data.shift(i)) / data.shift(i)  # 단순 수익률: (P(t) - P(t-i))/P(t-i), P = 종가
        if i == 1:
            temp = momentum
        else:
            temp += momentum
    mom = temp / 12  # 위에서 구한 모든 모멘텀값을 더한 후 12로 나눔 (12개월 평균 모멘텀이 된다)
    return mom.fillna(0)

    # *** UPDATE: 20180815 ***#


# *** UPDATE: 20180815 ***#
def volatility(returns_data, window=12):
    # 변동성 계산
    # 보통 변동성 계산은 일년을 주기로 계산한다
    # 그래서 returns_data 월별로 resample된거라면 window를 12로 잡는다
    # (데이터가 일일 데이터면 보통 window를 200으로 잡는다)
    # (데이터가 일주일로 resample되었다면, window는 48을 잡는다)
    # (3개월/분기별로 resample 되었다면 window는 4로 잡는다)
    return returns_data.rolling(window=window).std().fillna(0)


# *** UPDATE: 20180816 ***#
def correlation(returns_data, window=12):
    corr = returns_data.copy()
    corr['Eq_weight'] = list(pd.DataFrame(corr.values.T * (1.0 / len(corr.columns))).sum())
    return corr.rolling(window=window).corr().ix[-1][:-1]


# *** UPDATE: 20180915 ***#
def score(cls_df, vol_df, include_correlation=False, do_rank=False):
    from algorithms.data import Data
    ms_data = Data('marketsignal')
    ms_data.request('bm')
    benchmark = ms_data.kospi_index

    benchmark_cls = benchmark[['date', 'cls_prc']]
    benchmark_cls.set_index('date', inplace=True)
    benchmark_cls.index = pd.to_datetime(benchmark_cls.index)
    benchmark_cls.rename(columns={'cls_prc': 'Benchmark'}, inplace=True)

    cls_df = pd.concat([cls_df, benchmark_cls], axis=1, sort=True)

    benchmark_vol = benchmark[['date', 'trd_qty']]
    benchmark_vol.set_index('date', inplace=True)
    benchmark_vol.index = pd.to_datetime(benchmark_vol.index)
    benchmark_vol.rename(columns={'trd_qty': 'Benchmark'}, inplace=True)

    vol_df = pd.concat([vol_df, benchmark_vol], axis=1, sort=True)

    vol = cls_df * vol_df
    vol_score = vol.rank(ascending=True, axis=1)
    vol_score = (vol_score / vol_score.max()) * 100

    base = cls_df.pct_change()
    base.fillna(0, inplace=True)

    mom = dual_momentum(base)
    mom_score = mom.rank(ascending=True, axis=1)
    mom_score = (mom_score / mom_score.max()) * 100

    volt = volatility(base, 200)
    volt_score = volt.rank(ascending=False, axis=1)
    volt_score = (volt_score / volt_score.max()) * 100

    total_score = vol_score + mom_score + volt_score

    if include_correlation:
        cor = correlation(base, 200)
        cor_score = cor.rank(ascending=False, axis=1)
        cor_score = (cor_score / cor_score.max()) * 100
        total_score = total_score + cor_score // 4
    else:
        total_score = total_score // 3

    if do_rank:
        total_score = total_score.rank(ascending=True, axis=1)

    total_score.fillna(0, inplace=True)

    return total_score

'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.utils import timezone
import pandas as pd

from algorithms.data import Data
from algorithms.utils import score


class MarketSignalProcessor:
    # *** UPDATE: 20180725 ***#
    def __init__(self, taskname, today_date=None):
        self.taskname = taskname.lower()

        if today_date == None:
            self.today_date = timezone.now().strftime('%Y%m%d')
        else:
            self.today_date = today_date

        self.data = Data('marketsignal')

    # *** UPDATE: 20180806 ***#
    def reduce(self):
        taskname = self.taskname
        if hasattr(self, taskname):
            reducer = getattr(self, taskname)
            response = reducer()
            return response
        else:
            return {'state': '{} 태스크는 없습니다'.format(taskname)}

    # *** UPDATE: 20180725 ***#
    def format_decimal(self, data):
        # x.xxxxxxxx... 형식의 float 숫자를 x.xx형식으로 변환하여 리턴
        return float(format(round(data, 2), '.2f'))

    # *** UPDATE: 20180725 ***#
    def change_to_pct(self, data):
        # 0.xxxxxxxx... 형식의 float 숫자를 xx.xx형식으로 변환하여 리턴 (%로 변환)
        return float(format(round(data, 4), '.4f')) * 100

    # *** Mined API #1 ***#
    # *** UPDATE: 20180823 ***#
    def calc_bm_info(self):
        ###########################################
        ##### Calculate Benchmark Information #####
        ###########################################

        # DESCRIPTION: 코스피, 코스닥 인덱스, 전일대비 가격변화, 1D 수익률 리턴
        # API ENDPOINT: /mined/api/<version>/?algorithm=MARKET&task=CALC_BM_INFO
        # DATA: 코스피 인덱스(kospi_index), 코스닥 인덱스(kosdaq_index)

        # ================================= #
        # RETURN:
        # return type: dictionary
        # -------- kospi_index: 코스피 인덱스
        # -------- kospi_change: 코스피 전일대비 가격(인덱스)변화
        # -------- kospi_rate: 코스피 1 Day 수익률(리턴)
        # -------- kosdaq_index: 코스닥 인덱스
        # -------- kosdaq_change: 코스닥 전일대비 가격(인덱스)변화
        # -------- kosdaq_rate: 코스닥 1 Day 수익률(리턴))
        # ================================= #

        data = self.data
        data.request('bm')

        kospi_index = data.kospi_index
        kospi_change = kospi_index.iloc[-1][0] - kospi_index.iloc[-2][0]
        kospi_rate = kospi_change / kospi_index.iloc[-2][0]
        kosdaq_index = data.kosdaq_index
        kosdaq_change = kosdaq_index.iloc[-1][0] - kosdaq_index.iloc[-2][0]
        kosdaq_rate = kosdaq_change / kosdaq_index.iloc[-2][0]

        ret = {
            'kospi_index': self.format_decimal(kospi_index.iloc[-1][0]),
            'kospi_change': self.format_decimal(kospi_change),
            'kospi_rate': self.change_to_pct(kospi_rate),
            'kosdaq_index': self.format_decimal(kosdaq_index.iloc[-1][0]),
            'kosdaq_change': self.format_decimal(kosdaq_change),
            'kosdaq_rate': self.change_to_pct(kosdaq_rate)
        }

        return ret

    def make_size_df(self):
        data = self.data
        data.request('size')

        rms_data = Data('rms')
        rms_data.request('close')

        kp_data = {
            'lg': data.kp_lg_cap_index,
            'md': data.kp_md_cap_index,
            'sm': data.kp_sm_cap_index
        }

        kd_data = {
            'lg': data.kd_lg_cap_index,
            'md': data.kd_md_cap_index,
            'sm': data.kd_sm_cap_index
        }

        kospi_cls_df = rms_data.kospi_cls_df.copy()
        kospi_vol_df = rms_data.kospi_vol_df.copy()
        kosdaq_cls_df = rms_data.kosdaq_cls_df.copy()
        kosdaq_vol_df = rms_data.kosdaq_vol_df.copy()

        for d in kp_data.items():
            tmp = d[1][['date', 'cls_prc']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'cls_prc': d[0]}, inplace=True)
            kospi_cls_df = pd.concat([kospi_cls_df, tmp], axis=1, sort=True)
            tmp = d[1][['date', 'trd_qty']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'trd_qty': d[0]}, inplace=True)
            kospi_vol_df = pd.concat([kospi_vol_df, tmp], axis=1, sort=True)

        for d in kd_data.items():
            tmp = d[1][['date', 'cls_prc']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'cls_prc': d[0]}, inplace=True)
            kosdaq_cls_df = pd.concat([kosdaq_cls_df, tmp], axis=1, sort=True)
            tmp = d[1][['date', 'trd_qty']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'trd_qty': d[0]}, inplace=True)
            kosdaq_vol_df = pd.concat([kosdaq_vol_df, tmp], axis=1, sort=True)

        return (kospi_cls_df, kospi_vol_df), (kosdaq_cls_df, kosdaq_vol_df)

    # *** Mined API #2 ***#
    # *** UPDATE: 20180915 ***#
    def calc_size_info(self):
        ######################################
        ##### Calculate Size Information #####
        ######################################

        # DESCRIPTION: 코스피/코스닥 대형주, 중형주, 소형주 인덱스, 마켓점수, 전일대비 가격변화, 1D 수익률 리턴
        # + 추가설명: 여기서 마켓점수는 모멘턴, 변동성, 상관관계 점수를 합친 것을 말한다
        # API ENDPOINT: /mined/api/<version>/?algorithm=MARKET&task=CALC_SIZE_INFO
        # DATA: 대형주 인덱스(large_cap_index), 중형주 인덱스(mid_cap_index), 소형주 인덱스(small_cap_index)

        (kospi_cls_df, kospi_vol_df), (kosdaq_cls_df, kosdaq_vol_df) = self.make_size_df()
        kp_total_score = score(kospi_cls_df, kospi_vol_df, include_correlation=False)
        kd_total_score = score(kosdaq_cls_df, kosdaq_vol_df, include_correlation=False)

        data = {
            'kp_lg_index': kospi_cls_df.iloc[-1]['lg'],
            'kp_lg_score': kp_total_score.iloc[-1]['lg'],
            'kp_lg_change': kp_total_score.iloc[-1]['lg'] - kp_total_score.iloc[-2]['lg'],
            'kp_lg_state': None,
            'kp_md_index': kospi_cls_df.iloc[-1]['md'],
            'kp_md_score': kp_total_score.iloc[-1]['md'],
            'kp_md_change': kp_total_score.iloc[-1]['md'] - kp_total_score.iloc[-2]['md'],
            'kp_md_state': None,
            'kp_sm_index': kospi_cls_df.iloc[-1]['sm'],
            'kp_sm_score': kp_total_score.iloc[-1]['sm'],
            'kp_sm_change': kp_total_score.iloc[-1]['sm'] - kp_total_score.iloc[-2]['sm'],
            'kp_sm_state': None,
            'kd_lg_index': kosdaq_cls_df.iloc[-1]['lg'],
            'kd_lg_score': kd_total_score.iloc[-1]['lg'],
            'kd_lg_change': kd_total_score.iloc[-1]['lg'] - kd_total_score.iloc[-2]['lg'],
            'kd_lg_state': None,
            'kd_md_index': kosdaq_cls_df.iloc[-1]['md'],
            'kd_md_score': kd_total_score.iloc[-1]['md'],
            'kd_md_change': kd_total_score.iloc[-1]['md'] - kd_total_score.iloc[-2]['md'],
            'kd_md_state': None,
            'kd_sm_index': kosdaq_cls_df.iloc[-1]['sm'],
            'kd_sm_score': kd_total_score.iloc[-1]['sm'],
            'kd_sm_change': kd_total_score.iloc[-1]['sm'] - kd_total_score.iloc[-2]['sm'],
            'kd_sm_state': None
        }

        for market in ['kp', 'kd']:
            for size in ['lg', 'md', 'sm']:
                key = '%s_%s_change' % (market, size)
                if data[key] > 0:
                    state = 'line_up'
                elif data[key] == 0:
                    state = 'line_middle'
                else:
                    state = 'line_down'
                data['%s_%s_state' % (market, size)] = state

        return data

    def make_style_df(self):
        data = self.data
        data.request('style')

        rms_data = Data('rms')
        rms_data.request('close')

        style_data = {
            'g': data.growth_index,
            'v': data.value_index,
            'y': data.yield_index,
            'q': data.quality_index,
            's': data.social_index
        }

        cls_df = pd.concat([rms_data.kospi_cls_df, rms_data.kosdaq_cls_df], axis=1, sort=True)
        vol_df = pd.concat([rms_data.kospi_vol_df, rms_data.kosdaq_vol_df], axis=1, sort=True)

        for d in style_data.items():
            tmp = d[1][['date', 'cls_prc']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'cls_prc': d[0]}, inplace=True)
            cls_df = pd.concat([cls_df, tmp], axis=1, sort=True)
            tmp = d[1][['date', 'trd_qty']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'trd_qty': d[0]}, inplace=True)
            vol_df = pd.concat([vol_df, tmp], axis=1, sort=True)

        return cls_df, vol_df

    # *** Mined API #3 ***#
    # *** UPDATE: 20180915 ***#
    def calc_style_info(self):
        #######################################
        ##### Calculate Style Information #####
        #######################################

        cls_df, vol_df = self.make_style_df()
        total_score = score(cls_df, vol_df, include_correlation=False)

        data = {
            'g_index': cls_df.iloc[-1]['g'],
            'g_score': total_score.iloc[-1]['g'],
            'g_change': total_score.iloc[-1]['g'] - total_score.iloc[-2]['g'],
            'g_state': None,
            'v_index': cls_df.iloc[-1]['v'],
            'v_score': total_score.iloc[-1]['v'],
            'v_change': total_score.iloc[-1]['v'] - total_score.iloc[-2]['v'],
            'v_state': None,
            'y_index': cls_df.iloc[-1]['y'],
            'y_score': total_score.iloc[-1]['y'],
            'y_change': total_score.iloc[-1]['y'] - total_score.iloc[-2]['y'],
            'y_state': None,
            'q_index': cls_df.iloc[-1]['q'],
            'q_score': total_score.iloc[-1]['q'],
            'q_change': total_score.iloc[-1]['q'] - total_score.iloc[-2]['q'],
            'q_state': None,
            's_index': cls_df.iloc[-1]['s'],
            's_score': total_score.iloc[-1]['s'],
            's_change': total_score.iloc[-1]['s'] - total_score.iloc[-2]['s'],
            's_state': None
        }

        for style in ['g', 'v', 'y', 'q', 's']:
            if data[style + '_change'] > 0:
                state = 'line_up'
            elif data[style + '_change'] == 0:
                state = 'line_middle'
            else:
                state = 'line_down'
            data[style + '_state'] = state

        return data

    def make_industry_df(self):
        data = self.data
        data.request('industry')

        rms_data = Data('rms')
        rms_data.request('close')

        ranked_industry = [k for (k, v) in sorted(data.industry_data.items(),
                                                  key=lambda x: x[1]['cls_prc'].iloc[-1],
                                                  reverse=True)][:3]

        industry_data = {
            'ind_1': data.industry_data[ranked_industry[0]],
            'ind_2': data.industry_data[ranked_industry[1]],
            'ind_3': data.industry_data[ranked_industry[2]]
        }

        cls_df = pd.concat([rms_data.kospi_cls_df, rms_data.kosdaq_cls_df], axis=1, sort=True)
        vol_df = pd.concat([rms_data.kospi_vol_df, rms_data.kosdaq_vol_df], axis=1, sort=True)

        for d in industry_data.items():
            tmp = d[1][['date', 'cls_prc']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'cls_prc': d[0]}, inplace=True)
            cls_df = pd.concat([cls_df, tmp], axis=1, sort=True)
            tmp = d[1][['date', 'trd_qty']]
            tmp.set_index('date', inplace=True)
            tmp.index = pd.to_datetime(tmp.index)
            tmp.rename(columns={'trd_qty': d[0]}, inplace=True)
            vol_df = pd.concat([vol_df, tmp], axis=1, sort=True)

        return cls_df, vol_df, ranked_industry

    # *** Mined API #4 ***#
    # *** UPDATE: 20180915 ***#
    def calc_industry_info(self):
        ##########################################
        ##### Calculate Industry Information #####
        ##########################################

        cls_df, vol_df, ranked_industry = self.make_industry_df()
        total_score = score(cls_df, vol_df, include_correlation=False)

        data = {
            'ind_1_name': ranked_industry[0],
            'ind_1_index': cls_df.iloc[-1]['ind_1'],
            'ind_1_score': total_score.iloc[-1]['ind_1'],
            'ind_1_change': total_score.iloc[-1]['ind_1'] - total_score.iloc[-2]['ind_1'],
            'ind_1_state': None,
            'ind_2_name': ranked_industry[1],
            'ind_2_index': cls_df.iloc[-1]['ind_2'],
            'ind_2_score': total_score.iloc[-1]['ind_2'],
            'ind_2_change': total_score.iloc[-1]['ind_2'] - total_score.iloc[-2]['ind_2'],
            'ind_2_state': None,
            'ind_3_name': ranked_industry[2],
            'ind_3_index': cls_df.iloc[-1]['ind_3'],
            'ind_3_score': total_score.iloc[-1]['ind_3'],
            'ind_3_change': total_score.iloc[-1]['ind_3'] - total_score.iloc[-2]['ind_3'],
            'ind_3_state': None
        }

        for industry in ['ind_1', 'ind_2', 'ind_3']:
            if data[industry + '_change'] > 0:
                state = 'line_up'
            elif data[industry + '_change'] == 0:
                state = 'line_middle'
            else:
                state = 'line_down'
            data[industry + '_state'] = state

        return data

    # *** Mined API #5 ***#
    # *** UPDATE: 20180920 ***#
    def make_rank_data(self):
        ##########################
        ##### Make Rank Data #####
        ##########################

        (kospi_cls_df, kospi_vol_df), (kosdaq_cls_df, kosdaq_vol_df) = self.make_size_df()
        style_cls_df, style_vol_df = self.make_style_df()
        industry_cls_df, industry_vol_df, ranked_industry = self.make_industry_df()

        cls_df = pd.concat([kospi_cls_df, kosdaq_cls_df, style_cls_df, industry_cls_df], axis=1, sort=True)
        vol_df = pd.concat([kospi_vol_df, kosdaq_vol_df, style_vol_df, industry_vol_df], axis=1, sort=True)

        total_rank = score(cls_df, vol_df, include_correlation=False, do_rank=True)

        self.data.redis_client.set('RANK_DATA', total_rank.to_msgpack(compress='zlib'))

        return total_rank

    # *** Mined API #6 ***#
    # *** UPDATE: 20180920 ***#
    def emit_buysell_signal(self):
        ###############################
        ##### Emit Buysell Signal #####
        ###############################

        # 매수, 매도 시그널은 심플하게 계산한다
        # 코스피, 코스닥에 대해서만 매수, 매도 시그널을 계산할 것이다.

        # 우선, 코스피, 코스닥에 대한 토탈 점수를 구해야한다 (혹은 데이터가 있어야 한다)
        # 토탈 점수 = (거래대금 점수 + 모멘텀 점수 + 변동성 점수 + 상관관계 점수) // 4

        # 코스피에 대해서 점수를 모두 나열하고, 현재 점수의 랭킹을 매긴다
        # 금방 계산한 랭킹으로 --> 랭킹 / 코스피 점수 전체수 를 계산한다
        # 0 ~ 0.50: C
        # 0.50 ~ 0.80: B
        # 0.80 ~ 1: A
        # 으로 먼저 레이팅(rating)을 준다

        # 레이팅을 구하였다면, 수익률 상승이나 하락이나 몇일 연속 지속되었는지 계산하여 준다
        # 예를 들어, 데이터가 0.01, 0.02, 0.03, -0.01이라면, 하락 지속 1일 그리고 총 하락 0.01인 것이다
        # 또, 0.01, -0.01, -0.02, -0.02이면, 하락 지속 3일 그리고 총 하락 수익률은: 1 - (1 - 0.01)*(1 - 0.02)*(1-0.02) 이다

        # 위의 모든 계산을 마쳤다면,
        # 코스닥에도 마찬가지로 진행한다!

        # 마지막에는,
        ##### 코스피/코스닥의 레이팅, 상승/하락, 지속 일수, 수익률을 리턴한다 #####

        (kospi_cls_df, kospi_vol_df), (kosdaq_cls_df, kosdaq_vol_df) = self.make_size_df()

        kp_score = score(kospi_cls_df, kospi_vol_df, include_correlation=False, do_rank=True)
        kd_score = score(kosdaq_cls_df, kosdaq_vol_df, include_correlation=False, do_rank=True)

        return {
            'kospi_rating': 'A',
            'kospi_state': '상승',
            'kospi_state_last': 3,
            'kospi_state_return': 0.20,
            'kosdaq_rating': 'B',
            'kosdaq_state': '하락',
            'kosdaq_state_last': 2,
            'kosdaq_state_return': 0.04
        }

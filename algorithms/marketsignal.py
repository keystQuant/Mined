'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from datetime import datetime
import pandas as pd
import numpy as np

from algorithms.data import Data


class MarketSignalProcessor:
    '''

    **설명: 마켓시그널 페이지에 들어가는 요소들을 모두 계산하여 리턴해주는 데이터 분석 엔진

    **태스크:
    1. 시장별: 코스피, 코스닥 인덱스, 전일대비 가격변화, 1D 수익률 리턴
    2. 사이즈별: 대형주, 중형주, 소형주 인덱스, 마켓점수, 전일대비 가격변화, 1D 수익률 리턴
    3. 스타일별: 성장주, 가치주, 배당주, 퀄리티주, 사회책임경영주 인덱스, 마켓점수, 전일대비 가격변화, 1D 수익률 리턴
    4. 산업별: 모든 산업별 인덱스, 마켓점수, 전일대비 가격변화, 1D 수익률 리턴

    '''

    #*** UPDATE: 20180725 ***#
    def __init__(self, taskname, today_date=None):
        self.taskname = taskname.lower() # 태스크 이름을 받아서 소문자로 바꾼다

        # 오늘 날짜를 인자로 받고, 아무값이 들어오지 않았다면 YYYYMMDD형식으로 직접 포맷하여
        # self.today_date로 새팅
        if today_date == None:
            self.today_date = datetime.now().strftime('%Y%m%d')
        else:
            self.today_date = today_date

        # 데이터베이스 혹은 캐시에서 데이터를 가져올 수 있도록 Data 인스턴스를 만들어준다.
        # 어떤 데이트를 필요로 하는지 알기 위해 'marketsignal'을 인자로 보내준다.
        self.data = Data('marketsignal')

    #*** UPDATE: 20180806 ***#
    def reduce(self):
        taskname = self.taskname
        # 클래스 내에 태스크명과 같은 함수 이름이 있는지 확인한다.
        if hasattr(self, taskname):
            reducer = getattr(self, taskname) # 태스크명과 같은 메소드를 리듀서라고 부른다
            response = reducer() # 리듀서를 실행시키고 반환된 값을 다시 리턴한다
            return response
        else:
            return { 'state': '{} 태스크는 없습니다'.format(taskname) }

    #*** UPDATE: 20180725 ***#
    def format_decimal(self, data):
        # x.xxxxxxxx... 형식의 float 숫자를 x.xx형식으로 변환하여 리턴
        return float(format(round(data, 2), '.2f'))

    #*** UPDATE: 20180725 ***#
    def change_to_pct(self, data):
        # 0.xxxxxxxx... 형식의 float 숫자를 xx.xx형식으로 변환하여 리턴 (%로 변환)
        return float(format(round(data, 4), '.4f')) * 100

    #*** Mined API #1 ***#
    #*** UPDATE: 20180725 ***#
    def calc_bm_info(self):
        #####################################
        ##### Get Benchmark Information #####
        #####################################

        # DESCRIPTION: 코스피, 코스닥 인덱스, 전일대비 가격변화, 1D 수익률 리턴
        # API ENDPOINT: /mined/api/<version>/?algorithm=MARKET&type=CALC_BM_INFO
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
        # 데이터는 판다스 데이터프레임 안에 있다
        kospi_index = data.kospi_index
        kosdaq_index = data.kosdaq_index

        print(kospi_index)

        # kospi_change = kospi_index[0] - kospi_index[1] # 전일대비 가격변화
        # kospi_rate = kospi_change/kospi_index[1] # 1 Day 수익률
        # kosdaq_change = kosdaq_index[0] - kosdaq_index[1]
        # kosdaq_rate = kosdaq_change/kosdaq_index[1]
        # # 리턴하는 값들은 딕셔너리에 넣어서 리턴
        # return {
        #     'kospi_index': self.format_decimal(kospi_index[0]),
        #     'kospi_change': self.format_decimal(kospi_change),
        #     'kospi_rate': self.change_to_pct(kospi_rate),
        #     'kosdaq_index': self.format_decimal(kosdaq_index[0]),
        #     'kosdaq_change': self.format_decimal(kosdaq_change),
        #     'kosdaq_rate': self.change_to_pct(kosdaq_rate)
        # }

    #*** Mined API #2 ***#
    #*** UPDATE: 20180726 ***#
    def get_size_info(self):
        #####################################
        ##### Get Size Information #####
        #####################################

        # DESCRIPTION: 코스피/코스닥 대형주, 중형주, 소형주 인덱스, 마켓점수, 전일대비 가격변화, 1D 수익률 리턴
        # + 추가설명: 여기서 마켓점수는 모멘턴, 변동성, 상관관계 점수를 합친 것을 말한다
        # API ENDPOINT: /mined/api/<version>/?algorithm=MARKET&type=CALC_SIZE_INFO
        # DATA: 대형주 인덱스(large_cap_index), 중형주 인덱스(mid_cap_index), 소형주 인덱스(small_cap_index)

        # ================================= #
        # RETURN:
        # return type: dictionary
        # -------- kp_lg_index: 코스피 대형주 인덱스
        # -------- kp_lg_score: 코스피 대형주 마켓점수
        # -------- kp_lg_change: 코스피 대형주 전일대비 가격(인덱스)변화

        # -------- kp_md_index: 코스피 중형주 인덱스
        # -------- kp_md_score: 코스피 중형주 마켓점수
        # -------- kp_md_change: 코스피 중형주 전일대비 가격(인덱스)변화

        # -------- kp_sm_index: 코스피 소형주 인덱스
        # -------- kp_sm_score: 코스피 소형주 마켓점수
        # -------- kp_sm_change: 코스피 소형주 전일대비 가격(인덱스)변화

        # -------- kd_lg_index: 코스닥 대형주 인덱스
        # -------- kd_lg_score: 코스닥 대형주 마켓점수
        # -------- kd_lg_change: 코스닥 대형주 전일대비 가격(인덱스)변화

        # -------- kd_md_index: 코스닥 중형주 인덱스
        # -------- kd_md_score: 코스닥 중형주 마켓점수
        # -------- kd_md_change: 코스닥 중형주 전일대비 가격(인덱스)변화

        # -------- kd_sm_index: 코스닥 소형주 인덱스
        # -------- kd_sm_score: 코스닥 소형주 마켓점수
        # -------- kd_sm_change: 코스닥 소형주 전일대비 가격(인덱스)변화
        # ================================= #

        data = self.data
        data.request('size')
        kp_lg_cap_index = data.kp_lg_cap_index
        kp_md_cap_index = data.kp_md_cap_index
        kp_sm_cap_index = data.kp_sm_cap_index
        kd_lg_cap_index = data.kd_lg_cap_index
        kd_md_cap_index = data.kd_md_cap_index
        kd_sm_cap_index = data.kd_sm_cap_index

        data = {
            'l_index': self.format_decimal(l_index),
            'l_score': l_scores[0],
            'l_change': l_scores[0] - l_scores[1],
            'm_index': self.format_decimal(m_index),
            'm_score': m_scores[0],
            'm_change': m_scores[0] - m_scores[1],
            's_index': self.format_decimal(s_index),
            's_score': s_scores[0],
            's_change': s_scores[0] - s_scores[1]
        }
        for size in ['l', 'm', 's']:
            if data[size + '_change'] > 0:
                state = 'line_up'
            elif data[size + '_change'] == 0:
                state = 'line_middle'
            else:
                state = 'line_down'
            data[size + '_state'] = state
        return data

    #*** Mined API #3 ***#
    #*** UPDATE: 20180811 ***#
    def _get_style_info(self):
        #####################################
        ##### Get Style Information #####
        #####################################

        # DESCRIPTION: 성장주, 가치주, 배당주, 퀄리티주, 사회책임경영주 인덱스, 마켓점수, 전일대비 가격변화, 1D 수익률 리턴
        # + 추가설명: 여기서 마켓점수는 모멘턴, 변동성, 상관관계 점수를 합친 것을 말한다
        # API ENDPOINT: /mined/api/<version>/?algorithm=MARKET&type=CALC_STYLE_INFO
        # DATA: 대형주 인덱스(large_cap_index), 중형주 인덱스(mid_cap_index), 소형주 인덱스(small_cap_index)

        # ================================= #
        # RETURN:
        # return type: dictionary
        # -------- kp_lg_index: 코스피 대형주 인덱스
        # -------- kp_lg_score: 코스피 대형주 마켓점수
        # -------- kp_lg_change: 코스피 대형주 전일대비 가격(인덱스)변화

        # -------- kp_md_index: 코스피 중형주 인덱스
        # -------- kp_md_score: 코스피 중형주 마켓점수
        # -------- kp_md_change: 코스피 중형주 전일대비 가격(인덱스)변화

        # -------- kp_sm_index: 코스피 소형주 인덱스
        # -------- kp_sm_score: 코스피 소형주 마켓점수
        # -------- kp_sm_change: 코스피 소형주 전일대비 가격(인덱스)변화

        # -------- kd_lg_index: 코스닥 대형주 인덱스
        # -------- kd_lg_score: 코스닥 대형주 마켓점수
        # -------- kd_lg_change: 코스닥 대형주 전일대비 가격(인덱스)변화

        # -------- kd_md_index: 코스닥 중형주 인덱스
        # -------- kd_md_score: 코스닥 중형주 마켓점수
        # -------- kd_md_change: 코스닥 중형주 전일대비 가격(인덱스)변화
        # ================================= #

        style_list = Index.objects.filter(category='ST').order_by('-date')[:4]
        score_list = MarketScore.objects.filter(name__in=['G', 'V']).order_by('-date')[:4]

        for style_inst in style_list:
            index_name = style_inst.name
            if index_name == 'G':
                g_index = style_inst.index
            elif index_name == 'V':
                v_index = style_inst.index

        g_scores, v_scores = [], []
        for score_inst in score_list:
            index_name = score_inst.name
            if index_name == 'G':
                g_scores.append(score_inst.total_score)
            elif index_name == 'V':
                v_scores.append(score_inst.total_score)

        data = {
            'g_index': self.format_decimal(g_index),
            'g_score': g_scores[0],
            'g_change': g_scores[0] - g_scores[1],
            'v_index': self.format_decimal(v_index),
            'v_score': v_scores[0],
            'v_change': v_scores[0] - v_scores[1]
        }
        for size in ['g', 'v']:
            if data[size + '_change'] > 0:
                state = 'line_up'
            elif data[size + '_change'] == 0:
                state = 'line_middle'
            else:
                state = 'line_down'
            data[size + '_state'] = state
        return data

    #*** Mined API #4 ***#
    def _get_industry_info(self):
        industry_qs = Index.objects.filter(category='I')
        last_date = industry_qs.order_by('-date').first().date
        ranked_index = [data.name for data in industry_qs.filter(date=last_date).order_by('-index')[:3]]
        if '' in ranked_index:
            ranked_index = [data.name for data in industry_qs.filter(date=last_date).order_by('-index')[:4]]
            ranked_index.remove('')

        industry_list = industry_qs.filter(name__in=ranked_index).order_by('-date')[:3]
        score_list = MarketScore.objects.filter(name__in=ranked_index).order_by('-date')[:6]

        for industry_inst in industry_list:
            index_name = industry_inst.name
            if index_name == ranked_index[0]:
                ind_1_index = industry_inst.name
            elif index_name == ranked_index[1]:
                ind_2_index = industry_inst.name
            elif index_name == ranked_index[2]:
                ind_3_index = industry_inst.name

        ind_1_scores, ind_2_scores, ind_3_scores = [], [], []
        for score_inst in score_list:
            index_name = score_inst.name
            if index_name == ranked_index[0]:
                ind_1_scores.append(score_inst.total_score)
            elif index_name == ranked_index[1]:
                ind_2_scores.append(score_inst.total_score)
            elif index_name == ranked_index[2]:
                ind_3_scores.append(score_inst.total_score)

        data = {
            'ind_1_index': ind_1_index,
            'ind_1_score': ind_1_scores[0],
            'ind_1_change': ind_1_scores[0] - ind_1_scores[1],
            'ind_2_index': ind_2_index,
            'ind_2_score': ind_2_scores[0],
            'ind_2_change': ind_2_scores[0] - ind_2_scores[1],
            'ind_3_index': ind_3_index,
            'ind_3_score': ind_3_scores[0],
            'ind_3_change': ind_3_scores[0] - ind_3_scores[1]
        }
        for size in ['ind_1', 'ind_2', 'ind_3']:
            if data[size + '_change'] > 0:
                state = 'line_up'
            elif data[size + '_change'] == 0:
                state = 'line_middle'
            else:
                state = 'line_down'
            data[size + '_state'] = state
        return data

    #*** Mined API #5 ***#
    def make_rank_data(self):
        date = datetime.now().strftime('%Y%m%d')
        date_cut = Info.objects.order_by('-date').first().date
        ind_list = [ind[0] for ind in Info.objects.filter(date=date_cut).distinct('industry').values_list('industry')]
        loop_list = ['KOSPI', 'KOSDAQ', 'L', 'M', 'S', 'G', 'V'] + ind_list

        ### temporary hotfix ###
        specs_date_cut = Specs.objects.order_by('-date').first().date

        for filter_by in loop_list:
            print(filter_by)
            if (filter_by == 'KOSPI') or (filter_by == 'KOSDAQ'):
                mkt_list = [data[0] for data in Ticker.objects.filter(market_type=filter_by).distinct('code').values_list('code')]
                queryset = Specs.objects.filter(date=specs_date_cut).filter(code__in=mkt_list).order_by('total_score').reverse()[:100]
            elif (filter_by == 'L') or (filter_by == 'M') or (filter_by == 'S'):
                s_list = [data[0] for data in Info.objects.filter(date=date_cut).filter(size_type=filter_by).values_list('code')]
                queryset = Specs.objects.filter(date=specs_date_cut).filter(code__in=s_list).order_by('total_score').reverse()[:100]
            elif (filter_by == 'G') or (filter_by == 'V'):
                st_list = [data[0] for data in Info.objects.filter(date=date_cut).filter(style_type=filter_by).values_list('code')]
                queryset = Specs.objects.filter(date=specs_date_cut).filter(code__in=st_list).order_by('total_score').reverse()[:100]
            else:
                i_list = [data[0] for data in Info.objects.filter(date=date_cut).filter(industry=filter_by).values_list('code')]
                queryset = Specs.objects.filter(date=specs_date_cut).filter(code__in=i_list).order_by('total_score').reverse()[:100]
            data_num = 1
            data_list = []
            for data in queryset:
                code = data.code
                name = Ticker.objects.filter(code=code).first().name
                momentum_score = data.momentum_score
                volatility_score = data.volatility_score
                volume_score = data.volume_score
                total_score = data.total_score
                rank_inst = RankData(filter_by=filter_by,
                                     date=date,
                                     num=data_num,
                                     code=code,
                                     name=name,
                                     momentum_score=momentum_score,
                                     volatility_score=volatility_score,
                                     volume_score=volume_score,
                                     total_score=total_score)
                data_list.append(rank_inst)
                data_num += 1
            RankData.objects.bulk_create(data_list)
            print('Successfully saved {} data'.format(filter_by))

    #*** Mined API #6 ***#
    def emit_buysell_signal(self):
        pass

    #*** Mined API #7 ***#
    def rate_index(self):
        pass

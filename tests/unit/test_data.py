'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import pytest

from algorithms.data import Data


## Data 객체 Test 시작 ##
@pytest.fixture
def data_instance():
    data_inst = Data()
    return data_inst


def test_cache_can_get_tickers(data_instance):
    d = data_instance
    tickers = d.get_val('INDEX_TICKERS')
    assert type(tickers) == list


def test_cache_can_get_dataframes(data_instance):
    d = data_instance
    # 요청 보내고자 하는 코드와 키값 정의
    code = '000020'
    key = '000020_OHLCV'
    df = d.get_val(key)  # 캐시에서 정보를 가져온다
    returned_code = df['code'][0]
    # DF의 code값이 요청한 값과 일치한지 본다
    assert code == returned_code


@pytest.fixture
def marketsignal_inst():
    ms_inst = Data('marketsignal')
    assert ms_inst.algorithm_type == 'marketsignal'
    return ms_inst


def test_data_inst_can_set_marketsignal_data(marketsignal_inst):
    d = marketsignal_inst
    # 마켓시그널을 알고리즘으로 새팅하면, 자동으로 bm, size, style, industry, tickers
    # 속성(리스트값)들을 생성한다
    assert type(d.bm) == list
    assert type(d.size) == list
    assert type(d.style) == list
    assert type(d.industry) == list
    assert type(d.tickers) == list


def test_data_inst_can_request_bm_data(marketsignal_inst):
    d = marketsignal_inst
    d.request('bm')
    assert hasattr(d, 'kospi_index')
    assert hasattr(d, 'kosdaq_index')


def test_data_inst_can_request_size_data(marketsignal_inst):
    d = marketsignal_inst
    d.request('size')
    assert hasattr(d, 'kp_lg_cap_index')
    assert hasattr(d, 'kd_lg_cap_index')


def test_data_inst_can_request_style_data(marketsignal_inst):
    d = marketsignal_inst
    d.request('style')
    assert hasattr(d, 'growth_index')
    assert hasattr(d, 'value_index')


def test_data_inst_can_request_industry_data(marketsignal_inst):
    d = marketsignal_inst
    d.request('industry')
    assert type(d.industry_data) == dict
    assert len(d.industry_data.keys()) == len(d.industry)  # 산업 데이터 딕셔너리와 산업 코드의 리스트 갯수가 같은지 본다

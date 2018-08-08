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
    df = d.get_val(key) # 캐시에서 정보를 가져온다
    returned_code = df['code'][0]
    # DF의 code값이 요청한 값과 일치한지 본다
    assert code == returned_code

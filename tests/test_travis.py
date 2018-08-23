'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import pytest


##### Travis CI에서 새로운 환경의 테스트가 제대로 인식되고 테스트되는지 테스트 #####

## Test 시작 ##
@pytest.fixture
def example_data():
    data = 'data from fixture'
    return data


def test_travis_works(example_data):
    assert example_data == 'data from fixture'

'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import pytest

## Test 시작 ##
@pytest.fixture
def example_data():
    data = 'data from fixture'
    return data

def test_travis_works(example_data):
    assert example_data == 'data from fixture'

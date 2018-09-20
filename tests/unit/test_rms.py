'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.test import TestCase
import pandas as pd

from algorithms.rms import RMSProcessor


class RMSTestCase(TestCase):
    def test_backtest_EAA(self):
        p = RMSProcessor('BACKTEST_EAA')
        result = p.reduce()
        self.assertIsNotNone(result)

    def test_score_data(self):
        p = RMSProcessor('SCORE_DATA')
        result = p.reduce()
        self.assertIsNotNone(result)
        assert len(result) == 2
        assert all(isinstance(r, pd.DataFrame) for r in result)

'''
Mined. Test

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.test import TestCase

from algorithms.marketsignal import MarketSignalProcessor


class MarketSignalTestCase(TestCase):
    def test_calc_bm_info(self):
        p = MarketSignalProcessor('calc_bm_info')
        result = p.reduce()
        self.assertIsNotNone(result)
        self.assertIn('kospi_index', result)
        self.assertIn('kospi_change', result)
        self.assertIn('kospi_rate', result)
        self.assertIn('kosdaq_index', result)
        self.assertIn('kosdaq_change', result)
        self.assertIn('kosdaq_rate', result)

    def test_get_size_info(self):
        p = MarketSignalProcessor('get_size_info')

    def test_get_style_info(self):
        p = MarketSignalProcessor('get_style_info')

    def test_get_industry_info(self):
        p = MarketSignalProcessor('get_industry_info')

    def test_make_rank_data(self):
        p = MarketSignalProcessor('make_rank_data')

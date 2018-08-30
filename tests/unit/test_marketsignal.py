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
        p = MarketSignalProcessor('CALC_BM_INFO')
        result = p.reduce()
        self.assertIsNotNone(result)
        self.assertIn('kospi_index', result)
        self.assertIn('kospi_change', result)
        self.assertIn('kospi_rate', result)
        self.assertIn('kosdaq_index', result)
        self.assertIn('kosdaq_change', result)
        self.assertIn('kosdaq_rate', result)

    # def test_calc_size_info(self):
    #     p = MarketSignalProcessor('CALC_SIZE_INFO')
    #     result = p.reduce()
    #     self.assertIsNotNone(result)
    #
    # def test_calc_style_info(self):
    #     p = MarketSignalProcessor('CALC_STYLE_INFO')
    #     result = p.reduce()
    #     self.assertIsNotNone(result)
    #
    # def test_calc_industry_info(self):
    #     p = MarketSignalProcessor('CALC_INDUSTRY_INFO')
    #     result = p.reduce()
    #     self.assertIsNotNone(result)
    #
    # def test_make_rank_data(self):
    #     p = MarketSignalProcessor('MAKE_RANK_DATA')
    #     result = p.reduce()
    #     self.assertIsNotNone(result)
    #
    # def test_emit_buysell_signal(self):
    #     p = MarketSignalProcessor('EMIT_BUYSELL_SIGNAL')
    #     result = p.reduce()
    #     self.assertIsNotNone(result)

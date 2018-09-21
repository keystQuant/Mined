'''
Mined. Test

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.test import TestCase
import pandas as pd

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

    def test_calc_size_info(self):
        p = MarketSignalProcessor('CALC_SIZE_INFO')
        result = p.reduce()
        self.assertIsNotNone(result)
        for market in ['kp', 'kd']:
            for size in ['lg', 'md', 'sm']:
                for kind in ['index', 'score', 'change', 'state']:
                    self.assertIsNotNone(result['%s_%s_%s' % (market, size, kind)])

    def test_calc_style_info(self):
        p = MarketSignalProcessor('CALC_STYLE_INFO')
        result = p.reduce()
        self.assertIsNotNone(result)
        for style in ['g', 'v', 'y', 'q', 's']:
            for kind in ['index', 'score', 'change', 'state']:
                self.assertIsNotNone(result['%s_%s' % (style, kind)])

    def test_calc_industry_info(self):
        p = MarketSignalProcessor('CALC_INDUSTRY_INFO')
        result = p.reduce()
        self.assertIsNotNone(result)
        for industry in ['ind_1', 'ind_2', 'ind_3']:
            for kind in ['name', 'index', 'score', 'change', 'state']:
                self.assertIsNotNone(result['%s_%s' % (industry, kind)])

    def test_make_rank_data(self):
        p = MarketSignalProcessor('MAKE_RANK_DATA')
        result = p.reduce()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

    def test_emit_buysell_signal(self):
        p = MarketSignalProcessor('EMIT_BUYSELL_SIGNAL')
        result = p.reduce()
        self.assertIsNotNone(result)
        for market in ['kospi', 'kosdaq']:
            for kind in ['rating', 'state', 'state_last', 'state_return']:
                self.assertIsNotNone(result['%s_%s' % (market, kind)])

'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
from django.test import TestCase

from algorithms.portfolio import PortfolioProcessor


class PortfolioTestCase(TestCase):
    def test_get_recent_stock_close_price(self):
        p = PortfolioProcessor('get_recent_stock_close_price', 'S', ['000020', '000030', '005930'], 10000000)
        test_stock = '000020'
        result = p.get_recent_stock_close_price(test_stock)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)

    def test_initial_distribution(self):
        p = PortfolioProcessor('initial_distribution', 'S', ['000020', '000030', '005930'], 10000000)
        p.initial_distribution()
        result = p.ratio_dict
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('000020', result)
        self.assertIn('000030', result)
        self.assertIn('005930', result)

    def test_redistribute(self):
        p = PortfolioProcessor('initial_distribution', 'S', ['000020', '000030', '005930'], 10000000)
        p.initial_distribution()
        p.redistribute()
        result = p.ratio_dict
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('000020', result)
        self.assertIn('000030', result)
        self.assertIn('005930', result)
        self.assertIn('ratio', result['000020'])
        self.assertIn('ratio', result['000030'])
        self.assertIn('ratio', result['005930'])

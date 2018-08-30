from django.test import TestCase

from algorithms.scanner import ScannerProcessor


class ScannerTestCase(TestCase):
    def test(self):
        p = ScannerProcessor('')
        result = p.reduce()
        self.assertIsNotNone(result)

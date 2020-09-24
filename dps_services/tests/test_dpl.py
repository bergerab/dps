from unittest import TestCase
from datetime import datetime, timedelta

from dplib import DataSeries, DPL

class TestDPL(TestCase):
    def test_basic(self):
        '''Basic evaluation of literals'''
        self.assertEqual(DPL.eval('1'), 1)
        self.assertEqual(DPL.eval('"a"'), 'a')

    def test_operators(self):
        '''Evaluation of operators and environment binding'''
        self.assertEqual(DPL.eval('29 + 2'), 31)
        self.assertEqual(DPL.eval('a + 2', { 'a': 3 }), 5)

    def test_window(self):
        # Window size = 1
        ds = DataSeries.from_list([1, 2, 3, 4, 5, 6])
        windows = DPL.eval('window(b, "1s")', { 'B': ds}).windows_to_list()
        self.assertEqual(
            windows,
            [[1], [2], [3], [4], [5], [6]]
        )

        # Even sized windows
        ds = DataSeries.from_list([1, 2, 3, 4, 5, 6])
        windows = DPL.eval('window(b, "2s")', { 'B': ds}).windows_to_list()
        self.assertEqual(
            windows,
            [[1, 2], [3, 4], [5, 6]]
        )

        # Odd sized windows
        ds = DataSeries.from_list([1, 2, 3, 4, 5, 6])
        windows = DPL.eval('window(b, "3s")', { 'B': ds}).windows_to_list()
        self.assertEqual(
            windows,
            [[1, 2, 3], [4, 5, 6]]
        )

        # Even sized window with non-multiple
        ds = DataSeries.from_list([1, 2, 3, 4, 5, 6, 7])
        windows = DPL.eval('window(b, "2s")', { 'B': ds}).windows_to_list()
        self.assertEqual(
            windows,
            [[1, 2], [3, 4], [5, 6], [7]]
        )

        # Odd sized window with non-multiple
        ds = DataSeries.from_list([1, 2, 3, 4, 5, 6, 7])
        windows = DPL.eval('window(b, "3s")', { 'B': ds}).windows_to_list()
        self.assertEqual(
            windows,
            [[1, 2, 3], [4, 5, 6], [7]]
        )

    def test_average(self):
        ds = DataSeries.from_list([1,2,3,4,5,6,7,8,9,10])
        avg1 = (1+2)/2
        avg2 = (3+4)/2
        avg3 = (5+6)/2
        avg4 = (7+8)/2
        avg5 = (9+10)/2
        self.assertEqual(list(DPL.eval('average(window(a, "2s"))', { 'a': ds })),
                         [avg1, avg1, avg2, avg2, avg3, avg3, avg4, avg4, avg5, avg5])

        # Should work when window is not a multiple of input size
        ds = DataSeries.from_list([1,2,3,4,5,6,7])
        avg4 = 7/1
        self.assertEqual(list(DPL.eval('average(window(a, "2s"))', { 'a': ds })),
                         [avg1, avg1, avg2, avg2, avg3, avg3, avg4])

    def test_if_exp(self):
        '''If expressions should call DataSeries.when'''
        test = DataSeries.from_list([True, False, False, True])
        A = DataSeries.from_list(['a', 'b', 'c', 'd'])
        B = DataSeries.from_list([9, 8, 7, 6])
        self.assertEqual(list(DPL.eval('A if test else B', { 'test': test, 'A': A, 'B': B })),
                         ['a', 8, 7, 'd'])

        # Normal if expressions should work, if the test is not a dataseries
        self.assertEqual(list(DPL.eval('A if 1 else B', { 'A': A, 'B': B })),
                         ['a', 'b', 'c', 'd'])
        self.assertEqual(list(DPL.eval('A if 0 else B', { 'A': A, 'B': B })),
                         [9, 8, 7, 6])

    def test_with_constants(self):
        A = DataSeries.from_list([1,2,3,4])
        self.assertEqual(list(DPL.eval('A*22', { 'A': A })), [1*22, 2*22, 3*22, 4*22])
        self.assertEqual(list(DPL.eval('A*2.13', { 'A': A })), [1*2.13, 2*2.13, 3*2.13, 4*2.13])
        self.assertEqual(list(DPL.eval('2.13*A', { 'A': A })), [2.13*1, 2.13*2, 2.13*3, 2.13*4])

        # Constants inside of a if expression
        T = DataSeries.from_list([True, True, False, False])
        self.assertEqual(list(DPL.eval('2.13*A if T else A*83.22', { 'A': A, 'T': T })), [2.13*1, 2.13*2, 3*83.22, 4*83.22])

    def test_time_parsing(self):
        '''Should be able to parse time strings for milliseconds, seconds, minutes, hours, and days.'''
        self.assertEqual(DPL.eval('"2ms"'), timedelta(milliseconds=2))
        self.assertEqual(DPL.eval('"1000ms"'), timedelta(milliseconds=1000))
        self.assertEqual(DPL.eval('"1s"'), timedelta(seconds=1))
        self.assertEqual(DPL.eval('"10s"'), timedelta(seconds=10))
        self.assertEqual(DPL.eval('"3m"'), timedelta(minutes=3))
        self.assertEqual(DPL.eval('"7h"'), timedelta(hours=7))
        self.assertEqual(DPL.eval('"8d"'), timedelta(days=8))

    def test_window_extraction(self):
        '''Should be able to extract the timedelta values from windows.'''
        dpl = DPL()
        dpl.parse('window(2, "1s")')
        self.assertEqual(set(dpl.get_windows()), {timedelta(seconds=1)})
        dpl.parse('window(window(3, "2m"), "1s")')
        self.assertEqual(set(dpl.get_windows()), {timedelta(minutes=2), timedelta(seconds=1)})

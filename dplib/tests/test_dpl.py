from unittest import TestCase
from datetime import datetime, timedelta

from dplib import Series, DPL

def make_series(n, plus=0):
    now = datetime.now()
    return Series([x + plus for x in range(n)],
                  [now + timedelta(seconds=x) for x in range(n)])

class TestDPL(TestCase):
    def test_aggregation_propagates_intermidiate_values(self):
        xs = [1, 2, 3, 4, 5, 6]
        series = Series(xs)
        agg = DPL.eval('avg(a)', {
            'a': series,
        })
        self.assertEqual(agg.get_value(), sum(xs)/len(xs))
        self.assertEqual(agg.get_series(), xs)        

        xs = [1, 2, 3, 4, 5, 6]
        ys = list(map(lambda x: x * 37, [1, 2, 3, 4, 5, 6]))
        series = Series(xs)
        agg = DPL.eval('avg(a * 37)', {
            'a': series,
        })
        self.assertEqual(agg.get_value(), sum(ys)/len(ys))
        self.assertEqual(agg.get_series(), ys)        

    def test_aggregation(self):
        xs = [1, 2, 3, 4, 5, 6]
        series = Series(xs)
        self.assertEqual(DPL.eval('avg(a)', {
            'a': series,
        }).get_value(), sum(xs)/len(xs))

        xs = [1, 2, 8, 4, 5, 6]
        series = Series(xs)
        self.assertEqual(DPL.eval('max(a)', {
            'a': series,
        }).get_value(), max(xs))

        xs = [1, 2, 8, 4, 5, 6]
        series = Series(xs)
        self.assertEqual(DPL.eval('min(a)', {
            'a': series,
        }).get_value(), min(xs))

        xs = [1, 2, 8, 4, 5, 6]
        ys = [8, 2, 3, 1, 4, 9]
        self.assertEqual(DPL.eval('min(a) + max(b)', {
            'a': Series(xs),
            'b': Series(ys),            
        }).get_value(), min(xs) + max(ys))

        xs = [1, 2, 8, 4, 5, 6]
        ys = [8, 2, 3, 1, 4, 9]
        self.assertEqual(DPL.eval('min(a) * 2 + max(b) / 8.3', {
            'a': Series(xs),
            'b': Series(ys),            
        }).get_value(), min(xs) * 2 + max(ys) / 8.3)

        print(DPL.eval('min(a) * 2 + max(b) / 8.3', {
            'a': Series(xs),
            'b': Series(ys),            
        }))
    
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
        series = make_series(6)
        windows = DPL.eval('window(b, "1s")', { 'B': series }).windows_to_list()
        self.assertEqual(
            windows,
            [[0], [1], [2], [3], [4]]
        )

        # Even sized windows
        series = make_series(6)        
        windows = DPL.eval('window(b, "2s")', { 'B': series }).windows_to_list()
        self.assertEqual(
            windows,
            [[0, 1], [2, 3]]
        )

        # Odd sized windows
        series = make_series(6)                
        windows = DPL.eval('window(b, "3s")', { 'B': series }).windows_to_list()
        self.assertEqual(
            windows,
            [[0, 1, 2]]
        )

        # Even sized window with non-multiple
        series = make_series(6)                        
        windows = DPL.eval('window(b, "2s")', { 'B': series }).windows_to_list()
        self.assertEqual(
            windows,
            [[0, 1], [2, 3]],
        )

        # Odd sized window with non-multiple
        series = make_series(7)                                
        windows = DPL.eval('window(b, "3s")', { 'B': series }).windows_to_list()
        self.assertEqual(
            windows,
            [[0, 1, 2], [3, 4, 5]],
        )

    def test_average(self):
        series = make_series(10, plus=1)
        avg1 = (1+2)/2
        avg2 = (3+4)/2
        avg3 = (5+6)/2
        avg4 = (7+8)/2
        avg5 = (9+10)/2
        self.assertEqual(list(DPL.eval('avg(window(a, "2s"))', { 'a': series })),
                         [avg1, avg2, avg3, avg4])

        # Should work when window is not a multiple of input size
        series = make_series(7, plus=1)        
        avg4 = 7/1
        self.assertEqual(list(DPL.eval('avg(window(a, "2s"))', { 'a': series })),
                         [avg1, avg2, avg3])

    def test_if_exp(self):
        '''If expressions should call Series.when'''
        test = Series([True, False, False, True])
        A = Series(['a', 'b', 'c', 'd'])
        B = Series([9, 8, 7, 6])
        self.assertEqual(list(DPL.eval('A if test else B', { 'test': test, 'A': A, 'B': B })),
                         ['a', 8, 7, 'd'])

        # Normal if expressions should work, if the test is not a dataseries
        self.assertEqual(list(DPL.eval('A if 1 else B', { 'A': A, 'B': B })),
                         ['a', 'b', 'c', 'd'])
        self.assertEqual(list(DPL.eval('A if 0 else B', { 'A': A, 'B': B })),
                         [9, 8, 7, 6])

    def test_with_constants(self):
        A = Series([1,2,3,4])
        self.assertEqual(list(DPL.eval('A*22', { 'A': A })), [1*22, 2*22, 3*22, 4*22])
        self.assertEqual(list(DPL.eval('A*2.13', { 'A': A })), [1*2.13, 2*2.13, 3*2.13, 4*2.13])
        self.assertEqual(list(DPL.eval('2.13*A', { 'A': A })), [2.13*1, 2.13*2, 2.13*3, 2.13*4])

        # Constants inside of a if expression
        T = Series([True, True, False, False])
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
        
test_suite = TestDPL

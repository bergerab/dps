from unittest import TestCase
from datetime import datetime, timedelta

from pandas.testing import assert_series_equal
import pandas as pd

from dplib.testing import SeriesAssertions
from dplib.series import Series
from dplib.dataset import Dataset

def make_times(n, t=None, step=None):
    t = datetime.now() if t is None else t
    step = (lambda x: timedelta(seconds=x)) if step is None else step
    return [t + step(x) for x in range(n)]

class TestSeries(TestCase, SeriesAssertions):
    def test_identity(self):
        ds = Series(range(10))
        self.assertEqual(list(ds), list(range(10)))
        ds = Series(range(234))
        self.assertEqual(list(ds), list(range(234)))

    def binop(self, f):
        ds = Series(range(1, 11))                    
        for y in range(1, 20):
            self.assertEqual(list(f(ds, y)), list(map(lambda x: f(x, y), range(1, 11))))
            ds = Series(range(1, 11))            
            self.assertEqual(list(f(y, ds)), list(map(lambda x: f(y, x), range(1, 11))))

    def test_add(self):
        self.binop(lambda x, y: x + y)

    def test_sub(self):
        self.binop(lambda x, y: x - y)

    def test_mul(self):
        self.binop(lambda x, y: x * y)
        
    def test_div(self):
        self.binop(lambda x, y: x / y)

    def test_floordiv(self):
        self.binop(lambda x, y: x // y)

    def test_lt(self):
        self.binop(lambda x, y: x < y)                                

    def test_lte(self):
        self.binop(lambda x, y: x <= y)                                

    def test_gt(self):
        self.binop(lambda x, y: x > y)

    def test_gte(self):
        self.binop(lambda x, y: x >= y)                                

    def test_eq(self):
        self.binop(lambda x, y: x == y)

    def test_neq(self):
        self.binop(lambda x, y: x != y)

    def test_and(self):
        ds1 = Series([True, True, False, False])
        ds2 = Series([True, False, True, False])
        self.assertEqual(list(ds1._and(ds2)), [True, False, False, False])
        self.assertEqual(list(ds1._and(True)), [True, True, False, False])
        self.assertEqual(list(ds1._and(False)), [False, False, False, False])        

    def test_or(self):
        ds1 = Series([True, True, False, False])
        ds2 = Series([True, False, True, False])
        self.assertEqual(list(ds1._or(ds2)), [True, True, True, False])
        self.assertEqual(list(ds1._or(True)), [True, True, True, True])
        self.assertEqual(list(ds1._or(False)), [True, True, False, False])        

    def test_power(self):
        A = Series(range(20, 30))
        B = Series(range(40, 50))
        self.assertEqual(list(A * B),
                         list(map(lambda xs: xs[0] * xs[1],
                                  zip(range(20, 30), range(40, 50)))))

    def test_max(self):
        ds = Series([1, 4, -3, 30, 23, 4, 39, 11])
        self.assertEqual(max(ds), 39)

    def test_min(self):
        ds = Series([1, -2, 10])
        self.assertEqual(min(ds), -2)

    def test_sum(self):
        ds = Series([1, -2, 10])
        self.assertEqual(sum(ds), 9)

    def test_when(self):
        times = make_times(4)
        series = Series([True, False, True, False], times=times)
        series = series.when('A', 'B')
        assert_series_equal(series.series, pd.Series(['A', 'B', 'A', 'B'], index=times))

    def test_windows(self):
        # Windows are created with full buckets of data
        # That is each window is filled until it exceeds the time window.
        # Any data that has not yet exceeded the window, goes into a series called "cout"

        times = make_times(7)
        series = Series(range(7), times).window(timedelta(seconds=2)).average()
        assert_series_equal(series.series, pd.Series([(0+1)/2, (2+3)/2, (4+5)/2], index=[times[0], times[2], times[4]]))
        assert_series_equal(series.cout, pd.Series([6], index=[times[6]]))

        times = make_times(4)
        series = Series(range(4), times).window(timedelta(seconds=2)).average()
        assert_series_equal(series.series, pd.Series([(0+1)/2], index=[times[0]]))
        assert_series_equal(series.cout, pd.Series([2,3], index=[times[2], times[3]]))                

        times = make_times(5)
        series = Series(range(5), times).window(timedelta(seconds=3)).average()
        assert_series_equal(series.series, pd.Series([(0+1+2)/3], index=[times[0]]))
        assert_series_equal(series.cout, pd.Series([3, 4], index=[times[3], times[4]]))        

        times = make_times(6)
        series = Series(range(6), times).window(timedelta(seconds=10)).average()
        self.assertEqual(list(series), [])
        assert_series_equal(series.cout, pd.Series(range(6), index=times))

        times = make_times(6)
        series = Series(range(6), times).window(timedelta(seconds=1)).average()
        assert_series_equal(series.series, pd.Series(range(5), index=times[:-1]), check_dtype=False)
        assert_series_equal(series.cout, pd.Series([5], index=[times[5]]))

        now = datetime.now()
        times = [now + timedelta(seconds=n) for n in [0.1, 0.3, 0.9, 0.99, 1, 1.12]]
        values = list(range(6))
        series = Series(values, times).window(timedelta(seconds=1)).average()
        assert_series_equal(series.series, pd.Series([sum(values[:5])/5], index=[times[0]]))
        assert_series_equal(series.cout, pd.Series([values[5]], index=[times[5]]))

    def test_carry(self):
        # First 7 values are in sequence, next 7 are in different sequence
        t1 = make_times(7, t=datetime.now() - timedelta(hours=1))
        s1 = Series(range(7), t1).window(timedelta(seconds=2)).average()
        assert_series_equal(s1.series, pd.Series([(0+1)/2, (2+3)/2, (4+5)/2], index=[t1[0], t1[2], t1[4]]))
        assert_series_equal(s1.cout, pd.Series([6], index=[t1[6]]))

        t2 = make_times(7, t=datetime.now())
        s2 = Series(range(7, 7+7), t2, cin=s1.cout).window(timedelta(seconds=2)).average()
        assert_series_equal(s2.series, pd.Series([6/1, (7+8)/2, (9+10)/2, (11+12)/2],
                                                 index=[t1[6], t2[0], t2[2], t2[4]]))
        assert_series_equal(s2.cout, pd.Series([13], index=[t2[6]]))

        # Times that are all in sequence
        times = make_times(14)
        values = list(range(14))
        t1 = times[:7]
        v1 = values[:7]
        s1 = Series(v1, t1).window(timedelta(seconds=2)).average()
        assert_series_equal(s1.series, pd.Series([(v1[0]+v1[1])/2, (v1[2]+v1[3])/2, (v1[4]+v1[5])/2],
                                                 index=[t1[0], t1[2], t1[4]]))
        assert_series_equal(s1.cout, pd.Series([v1[6]], index=[t1[6]]))
        
        t2 = times[-7:]
        v2 = values[-7:]
        s2 = Series(v2, t2, cin=s1.cout).window(timedelta(seconds=2)).average()
        assert_series_equal(s2.series, pd.Series([(v1[6]+v2[0])/2, (v2[1]+v2[2])/2, (v2[3]+v2[4])/2],
                                                 index=[t1[6], t2[1], t2[3]]))
        assert_series_equal(s2.cout, pd.Series([v2[5], v2[6]], index=[t2[5], t2[6]]))

    def test_series_eq(self):
        self.assertEqual(Series([1,2,3]), Series([1,2,3]))
        self.assertEqual(Series([1,2,3], cout=pd.Series([5,4])), Series([1,2,3], cout=pd.Series([5,4])))        
        self.assertFalse(Series([1,2,3]).equals(Series([1,3])))
        self.assertFalse(Series([1,2,3], cout=pd.Series([2, 3])).equals(Series([1,2,3], cout=pd.Series([3, 4]))))
        self.assertFalse(Series([1,2,3], cout=pd.Series([3])).equals(Series([1,2,3], cout=pd.Series([3, 4]))))
        self.assertFalse(Series([1,2,3,4,5], cout=pd.Series([3, 4])).equals(Series([1,2,3], cout=pd.Series([3, 4]))))
        self.assertFalse(Series([1,2,3,4,5], cout=pd.Series([3, 4])).equals(Series([1,2,3,4,5,6], cout=pd.Series([3, 4]))))
        now = datetime.now()
        times = [now + timedelta(seconds=n) for n in [1,2,3]]
        self.assertEqual(Series([1,2,3], times), Series([1,2,3], times))
        self.assertFalse(Series([1,2,3], times).equals(Series([1], times[:1])))
        self.assertFalse(Series([1,2,3], times).equals(Series([1, 2, 3], times[:1] + [datetime.now(), datetime.now()])))        
        
    def test_dataset_eq(self):
        self.assertEqual(Dataset({
            'a': Series([1])
        }), Dataset({
            'a': Series([1])
        }))

    def test_is_windowed(self):
        times = make_times(10)
        values = range(10)
        series = Series(values, times)
        self.assertTrue(series.window(timedelta(seconds=1)).is_windowed())
        self.assertFalse(series.is_windowed())

    def test_logical_operator_integration(self):
        series = Series([1, 2, 3, 4])
        self.assertSeriesEqual((series >= 2)._and(series <= 3),
                               Series([False, True, True, False]))

        series = Series([1, 2, 3, 4])
        self.assertSeriesEqual((series >= 2)._or(series <= 3),
                               Series([True, True, True, True]))

test_suite = TestSeries

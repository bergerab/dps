from unittest import TestCase
from datetime import datetime, timedelta

from dplib import DataSeries

class TestDataSeries(TestCase):
    def test_operators(self):
        time = datetime.now()        
        ds = DataSeries.from_list([1,2,3,4], start_time=time, delta_time=timedelta(seconds=2))
        self.assertEqual(ds.start_time(), time)
        self.assertEqual(ds.end_time(), time + timedelta(seconds=2)*3)
        self.assertEqual(ds.to_list(), [1,2,3,4])

    def test_pointwise_computations(self):
        ds1 = DataSeries.from_list([1,2])
        ds2 = DataSeries.from_list([3,4])
        ds3 = ds1 + ds2
        self.assertEqual((ds1 + ds2).to_list(), [1+3, 2+4])
        self.assertEqual((ds1 - ds2).to_list(), [1-3, 2-4])
        self.assertEqual((ds1 * ds2).to_list(), [1*3, 2*4])
        self.assertEqual((ds1 / ds2).to_list(), [1/3, 2/4])
        self.assertEqual((ds1 // ds2).to_list(), [1//3, 2//4])

    def test_windowed_computations(self):
        time = datetime.now()                
        ds = DataSeries()
        ds.add(1, time)
        ds.add(1.3, time + timedelta(seconds=0.1))
        ds.add(2, time + timedelta(seconds=1.1))
        dss = ds.time_window(timedelta(seconds=1))
        self.assertEqual(dss.average().to_list()[0], sum([1, 1.3])/2)
        self.assertEqual(dss.average().to_list()[1], 2)
        self.assertEqual(len(dss.average().to_list()), 2)

    def test_pointwise_computations_with_constants(self):
        ds = DataSeries.from_list([1,2])
#        self.assertEqual(list(ds*2), [2, 4])
    
    def test_when(self):
        '''`when` should take from A when T has a 1 (truthy value) and take from B when T has a 0 (non-truthy value).
        '''
        time = datetime.now()
        T = DataSeries.from_list([0, 0, 1, 1, 0, 1, 0, 0], time)
        A = DataSeries.from_list(['a', 'b', 'c', 'd', 'e', 'f', 'g'], time)
        B = DataSeries.from_list([11, 12, 13, 14, 15, 16, 17, 18, 19, 20], time)
        self.assertEqual(list(T.when(A, B)), [11, 12, 'c', 'd', 15, 'f', 17, 18])

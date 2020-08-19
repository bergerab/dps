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
    

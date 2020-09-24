from unittest import TestCase
from datetime import datetime, timedelta

import numpy as np

from dplib import DataSeries

def generate_sine_wave(t0=0, periods=2, offset=0.0, dt=1e-5, amplitude=2, base_harmonic=40):
    '''
    Generate discrete samples of a pure sine wave.
    '''
    cycles = 0.025*periods
    N = int((cycles-t0)/dt)
    time = np.linspace(0.0, cycles, N)
    return [time, amplitude*np.sin(2.0*np.pi*base_harmonic*time) + offset]

def plot_wave(time, wave):
    '''
    This code is not used, it is included for interactive testing
    Using this function requires installing matplotlib
    '''
    import matplotlib.pyplot as plot
    plot.plot(time, wave)
    plot.title('Wave')
    plot.xlabel('Time')
    plot.ylabel('Amplitude')
    plot.grid(True, which='both')
    plot.axhline(y=0, color='k')
    plot.show()

def thd(wave):
    '''
    An unused THD calculation I found online.
    I interactively plotted this to compare it to the results of ours.
    '''
    abs_yf = np.abs(np.fft.fft(wave))
    abs_data = abs_yf[1:int(len(abs_yf)/2)]
    sq_sum=0.0
    for r in range( len(abs_data)):
       sq_sum = sq_sum + (abs_data[r])**2

    sq_harmonics = sq_sum -(max(abs_data))**2.0
    thd = 100*sq_harmonics**0.5 / max(abs_data)

    return thd

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
        avg1 = (1 + 1.3)/2
        avg2 = 2/1
        self.assertEqual(dss.average().to_list(), [avg1, avg1, avg2])

    def test_comparison_overload(self):
        ds = DataSeries.from_list([1,2,3,4,5,6,7,8])
        self.assertEqual(list(ds<4), [True, True, True, False, False, False, False, False])
        self.assertEqual(list(ds>4), [False, False, False, False, True, True, True, True])
        self.assertEqual(list(ds>=4), [False, False, False, True, True, True, True, True])
        self.assertEqual(list(ds<=4), [True, True, True, True, False, False, False, False])

    def test_bool_op(self):
        ds1 = DataSeries.from_list([True, False, True, False])
        ds2 = DataSeries.from_list([True, False, False, True])        
        self.assertEqual(list(ds1._and(ds2)), [True, False, False, False])
        ds1 = DataSeries.from_list([True, False, True, False])
        ds2 = DataSeries.from_list([True, False, False, True])        
        self.assertEqual(list(ds1._or(ds2)), [True, False, True, True])

    def test_pointwise_computations_with_constants(self):
        a = 7
        b = 13
        c = 9
        ds = DataSeries.from_list([a,b])
        self.assertEqual(list(c+ds), [c+a, c+b])
        self.assertEqual(list(ds+c), [a+c, b+c])
        self.assertEqual(list(c-ds), [c-a, c-b])
        self.assertEqual(list(ds-c), [a-c, b-c])        
        self.assertEqual(list(c*ds), [c*a, c*b])
        self.assertEqual(list(ds*c), [a*c, b*c])
        self.assertEqual(list(c/ds), [c/a, c/b])
        self.assertEqual(list(ds/c), [a/c, b/c])
        self.assertEqual(list(c//ds), [c//a, c//b])
        self.assertEqual(list(ds//c), [a//c, b//c])

    def test_negate(self):
        ds = DataSeries.from_list([1,2,3,4])        
        self.assertEqual(list(-ds), [-1,-2,-3,-4])

    def test_thd(self):
        time, wave = generate_sine_wave()

        # THD of a perfect sine wave should be very close to 0
        ds = DataSeries.from_list(list(wave), timedelta(seconds=1/len(wave)))
        self.assertLess(ds.thd(40) * 100, 0.01) # 0.01%
    
    def test_when(self):
        '''`when` should take from A when T has a 1 (truthy value) and take from B when T has a 0 (non-truthy value).
        '''
        time = datetime.now()
        T = DataSeries.from_list([0, 0, 1, 1, 0, 1, 0, 0], time)
        A = DataSeries.from_list(['a', 'b', 'c', 'd', 'e', 'f', 'g'], time)
        B = DataSeries.from_list([11, 12, 13, 14, 15, 16, 17, 18, 19, 20], time)
        self.assertEqual(list(T.when(A, B)), [11, 12, 'c', 'd', 15, 'f', 17, 18])

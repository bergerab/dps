from unittest import TestCase
from datetime import datetime, timedelta

import numpy as np
import matplotlib.pyplot as plot

from dplib import DataSeries

def generate_sine_wave(t0=0, periods=2, offset=0.0, dt=1e-5, amplitude=2, base_harmonic=40):
    cycles = 0.025*periods
    N = int((cycles-t0)/dt)
    time = np.linspace(0.0, cycles, N)
    return [time, amplitude*np.sin(2.0*np.pi*base_harmonic*time) + offset]

def plot_wave(time, wave):
    plot.plot(time, wave)
    plot.title('Wave')
    plot.xlabel('Time')
    plot.ylabel('Amplitude = sin(time)')
    plot.grid(True, which='both')
    plot.axhline(y=0, color='k')
    plot.show()

#print("freq is" + str(scipy.fftpack.fftfreq(sampled_data, dt )  ))
#As far as I know, THD=sqrt(sum of square magnitude of
#harmonics+noise)/Fundamental value (Is it correct?)So I'm
#just summing up square of all frequency data obtained from FFT,
#sqrt() them and dividing them with fundamental frequency value.

def thd(wave):
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
        self.assertEqual(dss.average().to_list()[0], sum([1, 1.3])/2)
        self.assertEqual(dss.average().to_list()[1], 2)
        self.assertEqual(len(dss.average().to_list()), 2)

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

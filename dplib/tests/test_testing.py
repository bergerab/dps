from unittest import TestCase
from datetime import datetime, timedelta

import numpy as np

from dplib import Series, DPL
from dplib.testing import generate_sine_wave

def plot_wave(time, wave):
    '''
    This code is not used by the unit tests, but it is included for interactive testing.
    (Using this function requires installing matplotlib)
    '''
    import matplotlib.pyplot as plot
    plot.plot(time, wave)
    plot.title('Wave')
    plot.xlabel('Time')
    plot.ylabel('Amplitude')
    plot.grid(True, which='both')
    plot.axhline(y=0, color='k')
    plot.show()

def plot_wave_fft(time, wave):
    import matplotlib.pyplot as plot
    ft = np.fft.fft(wave)
    freq = np.fft.fftfreq(len(wave), time[1] - time[0])

    plot.ylabel("Amplitude")
    plot.xlabel("Frequency [Hz]")
    plot.plot(freq, np.abs(ft))
    plot.show()

def get_fundamental_frequency(times, data):
    ft = np.abs(np.fft.fft(data))
    freq = np.abs(np.fft.fftfreq(len(data), times[1] - times[0]))
    
    m = 0
    f = 0
    for i in freq:
        val = ft[int(i)]
        if val > m:
            m = val
            f = i
    return f

class TestTesting(TestCase):
    def test_generate_sine_wave_has_proper_len(self):
        times, data = generate_sine_wave(sample_rate=10000,
                                         duration=1)
        self.assertEqual(len(data), 10000)
        self.assertEqual(len(times), 10000)        

        times, data = generate_sine_wave(sample_rate=20000,
                                         duration=1)
        self.assertEqual(len(data), 20000)
        self.assertEqual(len(times), 20000)        

        times, data = generate_sine_wave(sample_rate=20000,
                                         duration=2)
        self.assertEqual(len(data), 20000*2)
        self.assertEqual(len(times), 20000*2)

    def test_generate_sine_wave_has_proper_freq(self):
        times, data = generate_sine_wave(sample_rate=20000,
                                         duration=1,
                                         frequency=50)
        self.assertEqual(50, get_fundamental_frequency(times, data))

        times, data = generate_sine_wave(sample_rate=10000,
                                         duration=1,
                                         frequency=35)
        self.assertEqual(35, get_fundamental_frequency(times, data))

        times, data = generate_sine_wave(sample_rate=5000,
                                         duration=3,
                                         frequency=98)
        self.assertEqual(98, get_fundamental_frequency(times, data))
        
test_suite = TestTesting

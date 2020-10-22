from unittest import TestCase
from datetime import datetime, timedelta

import numpy as np

from dplib import Series, DPL
from dplib.testing import SeriesAssertions, generate_sine_wave

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

class TestBuiltins(TestCase, SeriesAssertions):
    def test_thd(self):
        # Add a base harmonic without any other harmonics
        # Should have THD of 0%.
        times, data = generate_sine_wave(duration=15,
                                         sample_rate=1000,
                                         frequency=30)
        now = datetime.now()
        times = list(map(lambda n: now + timedelta(seconds=n), times))
        series = DPL.eval('thd(window(A, "1s"), 30)', {
            'A': Series(data, times),
        })
        for value in series:
            self.assertLess(value, 1e-10) # ~0%


        # Add a harmonic with the same amplitude as the base
        # Should have THD of 100%.
        _, data2 = generate_sine_wave(duration=15,
                                         sample_rate=1000,
                                         frequency=30*30)
        data += data2
        series = DPL.eval('thd(window(A, "1s"), 30)', {
            'A': Series(data, times),
        })
        for value in series:
            self.assertGreater(value, 99) # ~100%

        times, data = generate_sine_wave(duration=15,
                                         sample_rate=1000,
                                         frequency=30)

        # Add a harmonic with the 1/10 of the amplitude of the base
        # Should have THD of 10%.
        times, data = generate_sine_wave(duration=15,
                                         sample_rate=1000,
                                         frequency=60)
        _, data2 = generate_sine_wave(duration=15,
                                      sample_rate=1000,
                                      frequency=60*60*60)
        data2 = data2/10 # 1/10 of the amplitude of the base
        data += data2
        times = list(map(lambda n: now + timedelta(seconds=n), times))
        series = DPL.eval('thd(window(A, "1s"), 60)', {
            'A': Series(data, times),
        })
        for value in series:
            print(value)
#            self.assertTrue(9.9999 < value < 10.00001) # ~10%
        # Add two harmonics with 1/9 and 1/8 the amplitude of the base
        # Should have THD of 17%.
        times, data = generate_sine_wave(duration=5,
                                         sample_rate=10000,
                                         frequency=60)
        _, data2 = generate_sine_wave(duration=5,
                                      sample_rate=10000,
                                      frequency=60*60)
        data += data2/9 # 1/9 of the amplitude of the base
        _, data3 = generate_sine_wave(duration=5,
                                      sample_rate=10000,
                                      frequency=60*60*60)
        data += data3/8  # 1/8 of the amplitude of the base
        times = list(map(lambda n: now + timedelta(seconds=n), times))
        series = DPL.eval('thd(window(A, "1s"), 60)', {
            'A': Series(data, times),
        })
        for value in series:
            self.assertTrue(16 < value < 17.1) # ~17%

        # Add two harmonics with 1/40 and 1/37 the amplitude of the base
        # Should have THD of 77%.
        times, data = generate_sine_wave(duration=5,
                                         sample_rate=10000,
                                         frequency=90)
        _, data2 = generate_sine_wave(duration=5,
                                      sample_rate=10000,
                                      frequency=90*90)
        data += data2/40 # 1/40 of the amplitude of the base
        _, data3 = generate_sine_wave(duration=5,
                                      sample_rate=10000,
                                      frequency=90*90*90)
        data += data3/8  # 1/37 of the amplitude of the base
        times = list(map(lambda n: now + timedelta(seconds=n), times))
        series = DPL.eval('thd(window(A, "1s"), 90)', {
            'A': Series(data, times),
        })
        for value in series:
            print(value)
#            self.assertTrue(76 < value < 77.1) # ~77%

# TODO: Follow equation for THD_F. Everything seems to be working
# Add a "self.assertEqualsPlusMinus(x, y, threshold=0.001)

# 0.16724436507

test_suite = TestBuiltins

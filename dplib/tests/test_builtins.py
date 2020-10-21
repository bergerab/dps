from unittest import TestCase
from datetime import datetime, timedelta

import numpy as np

from dplib import Series, DPL
from dplib.testing import SeriesAssertions

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

class TestBuiltins(TestCase, SeriesAssertions):
    def test_thd2(self):
        times, data = generate_sine_wave(dt=0.000005)
        now = datetime.now()
        times = list(map(lambda n: now + timedelta(minutes=n), times))
        print('samples: ', len(times))
        print(DPL.eval('thd2(window(A, "1s"), 40, 5000)', {
            'A': Series(data, times),
        }).series)

test_suite = TestBuiltins

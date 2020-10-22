from unittest import TestCase
from datetime import datetime, timedelta

import numpy as np

from dplib import Series, DPL
from dplib.testing import SeriesAssertions, WaveformGenerator

class TestBuiltins(TestCase):
    def assertEqualsWithTolerance(self, i1, i2, tolerance=1e-7):
        '''
        Assert the difference between `i1` and `i2` is less than `tolerance`
        '''
        self.assertLess(abs(i2 - i1), tolerance)
    
    def test_thd_0_percent(self):
        ''' Adding a base harmonic without any other harmonics should have THD of 0%. '''
        waveform = WaveformGenerator() \
            .add(frequency=30, amplitude=1) \
            .generate(sample_rate=1000, duration=15)
        series = DPL.eval('thd(window(A, "1s"), 30)', {
            'A': waveform.to_series(),
        })
        
        for value in series:
            self.assertEqualsWithTolerance(value, 0)

    def test_thd_100_percent(self):
        ''' Adding a harmonic with the same amplitude as the base should have THD of 100%. '''
        waveform = WaveformGenerator() \
            .add(frequency=30, amplitude=1) \
            .add(frequency=30*30, amplitude=1) \
            .generate(sample_rate=1000, duration=15)
        series = DPL.eval('thd(window(A, "1s"), 30)', {
            'A': waveform.to_series()
        })
        
        actual_thd = 100 * np.sqrt(np.power(1, 2))/np.power(1, 2)
        self.assertEqual(actual_thd, 100)
        for value in series:
            self.assertEqualsWithTolerance(value, 100)

    def test_thd_one_harmonic(self):        
        ''' Adding a harmonic with the 1/10 of the amplitude of the base should have THD of 10%. '''
        waveform = WaveformGenerator() \
            .add(frequency=60, amplitude=1) \
            .add(frequency=60*60, amplitude=1/10) \
            .generate(sample_rate=1000, duration=15)
        series = DPL.eval('thd(window(A, "1s"), 60)', {
            'A': waveform.to_series()
        })

        actual_thd = 100 * np.sqrt(np.power(1/10, 2))/np.power(1, 2)
        for value in series:
            self.assertEqualsWithTolerance(value, actual_thd)

    def test_thd_two_harmonics(self):        
        waveform = WaveformGenerator() \
            .add(frequency=60, amplitude=1) \
            .add(frequency=60*60, amplitude=1/8) \
            .add(frequency=60*60*60, amplitude=1/9) \
            .generate(sample_rate=1000, duration=15)
        series = DPL.eval('thd(window(A, "1s"), 60)', {
            'A': waveform.to_series(),
        })

        actual_thd = 100 * np.sqrt(np.power(1/9, 2) + np.power(1/8, 2))/np.power(1, 2)
        for value in series:
            self.assertEqualsWithTolerance(value, actual_thd)

    def test_thd_two_small_harmonics(self):        
        waveform = WaveformGenerator() \
            .add(frequency=90, amplitude=1) \
            .add(frequency=90*90, amplitude=1/40) \
            .add(frequency=90*90*90, amplitude=1/37) \
            .generate(sample_rate=1000, duration=15)
        series = DPL.eval('thd(window(A, "1s"), 90)', {
            'A': waveform.to_series(),
        })
        
        actual_thd = 100 * np.sqrt(np.power(1/40, 2) + np.power(1/37, 2))/np.power(1, 2)
        for value in series:
            self.assertEqualsWithTolerance(value, actual_thd)

    def test_thd_three_harmonics(self):        
        waveform = WaveformGenerator() \
            .add(frequency=30, amplitude=1) \
            .add(frequency=30*30, amplitude=1/3) \
            .add(frequency=30*30*30, amplitude=1/4) \
            .add(frequency=30*30*30*30, amplitude=1/9) \
            .generate(sample_rate=10000, duration=15)
        series = DPL.eval('thd(window(A, "1s"), 30)', {
            'A': waveform.to_series(),
        })
        
        actual_thd = 100 * np.sqrt(np.power(1/3, 2) +
                                    np.power(1/4, 2) +
                                    np.power(1/9, 2))/np.power(1, 2)
        for value in series:
            self.assertEqualsWithTolerance(value, actual_thd)

test_suite = TestBuiltins

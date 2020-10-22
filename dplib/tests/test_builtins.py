from unittest import TestCase
from datetime import datetime, timedelta
import functools

import numpy as np

from dplib import Series, DPL
from dplib.testing import SeriesAssertions, WaveformGenerator

class TestBuiltins(TestCase):
    def test_thd_0_percent(self):
        '''
        When there are no harmonics present, the THD should be 0%.
        '''
        thd = self.thd_test(base_harmonic=30,
                      base_amplitude=1,
                      sample_rate=1000,
                      harmonics={})
        self.assertEqual(thd, 0)        

    def test_thd_100_percent(self):
        '''
        When there is a harmonic with the same amplitude as the base harmonic, THD should be 100%.

        This test creates a waveform with a base harmonic of 30 and an amplitude of 1, and one harmonic
        (the 1st harmonic). The 1st harmonic has an amplitude of 1. This matches the base harmonic's amplitude,
        which means the THD should be 1/1 = 100%.
        '''
        thd = self.thd_test(base_harmonic=30,
                      base_amplitude=1,
                      sample_rate=1000,
                      harmonics={
                          1: 1,
                      })
        self.assertEqual(thd, 100)

    def test_thd_two_harmonics(self):
        '''
        When there are two harmonics, their amplitudes should be included in the THD.

        This test creates a waveform with a base harmonic of 30 that has an amplitude of 1,
        and two harmonics (the 1st and 2nd). The 1st harmonic has an amplitude of 1/3, and the 2nd harmonic has
        an amplitude of 1/4.
        '''
        self.thd_test(base_harmonic=30,
                      base_amplitude=1,
                      duration=2,
                      sample_rate=1000,
                      harmonics={
                          1: 1/3,
                          2: 1/4,
                      })

    def test_thd_three_harmonics(self):
        '''
        When there are three harmonics, their amplitudes should be included in the THD.

        This test creates a waveform with a base harmonic of 30 that has an amplitude of 1,
        and three harmonics (the 1st, 2nd, and 8th). The 1st harmonic has an amplitude of 1/3, 
        and the 2nd harmonic has an amplitude of 1/4, and the 8th harmonic has an amplitude of
        1/9.
        '''
        self.thd_test(base_harmonic=30,
                      base_amplitude=1,
                      duration=2,
                      sample_rate=1000,
                      harmonics={
                          1: 1/3,
                          2: 1/4,
                          8: 1/9,
                      })

    def test_thd_four_harmonics(self):
        '''
        When there are four harmonics, their amplitudes should be included in the THD.
        '''
        self.thd_test(base_harmonic=60,
                      base_amplitude=1,
                      duration=2,
                      sample_rate=5000,
                      harmonics={
                          1: 1/11,
                          2: 1/19,
                          8: 1/9,
                          13: 1/4,
                      })

    def test_thd_long_duration(self):
        '''
        THD should still work when the duration of the signal is long.
        '''
        self.thd_test(base_harmonic=60,
                      base_amplitude=1,
                      duration=20,
                      sample_rate=500,
                      harmonics={
                          1: 1/3,
                      })

    def test_thd_window_size(self):
        self.thd_test(base_harmonic=10,
                      base_amplitude=1,
                      duration=5,
                      sample_rate=100,
                      window_size="2s",
                      harmonics={
                          1: 1/3,
                      })
        self.thd_test(base_harmonic=10,
                      base_amplitude=1,
                      duration=30,
                      sample_rate=100,
                      window_size="10s",
                      harmonics={
                          1: 1/23,
                          2: 1/8,
                      })
        self.thd_test(base_harmonic=10,
                      base_amplitude=1,
                      duration=100,
                      sample_rate=100,
                      window_size="1m",
                      harmonics={
                          1: 1/23,
                          2: 1/8,
                      })
        self.thd_test(base_harmonic=50,
                      base_amplitude=1,
                      duration=20,
                      sample_rate=1000,
                      window_size="10s",
                      harmonics={
                          1: 1/23,
                          2: 1/8,
                      })

    def assertEqualsWithTolerance(self, i1, i2, tolerance=1e-7):
        '''
        Assert the difference between `i1` and `i2` is less than `tolerance`
        '''
        self.assertLess(abs(i2 - i1), tolerance)

    def thd_test(self, base_harmonic=30, base_amplitude=1, sample_rate=1000, harmonics={}, duration=5, window_size="1s"):
        gen = WaveformGenerator() \
            .add(frequency=base_harmonic, amplitude=base_amplitude)
        for nth_harmonic, amplitude in harmonics.items():
            frequency = base_harmonic * (nth_harmonic + 1)
            gen.add(frequency=frequency, amplitude=amplitude)
        waveform = gen.generate(sample_rate=sample_rate, duration=duration)
        series = DPL.eval(f'thd(window(A, "{window_size}"), {base_harmonic})', {
            'A': waveform.to_series(),
        })
        sum_of_squares = np.sqrt(functools.reduce(lambda a, b: a + np.power(b, 2), harmonics.values(), 0))
        # Theoretical THD is the THD you would get if you did the calculation by hand
        # When doing the THD in Python, you pick up very small amounts of harmonics (around 1e-13 in amplitude)
        # Even what no harmonic is present, so the THD will be slightly off from the theoretical THD.
        # This is why I check equals with a tolerance, to ignore any noise from floating point rounding errors.
        theoretical_thd = 100 * sum_of_squares / np.power(base_amplitude, 2)
        for value in series:
            self.assertEqualsWithTolerance(value, theoretical_thd)
        return theoretical_thd

test_suite = TestBuiltins

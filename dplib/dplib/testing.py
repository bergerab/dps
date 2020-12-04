from datetime import datetime, timedelta

from .result import Result
from .series import Series

from pandas.testing import assert_series_equal
import numpy as np

class SeriesAssertions:
    def assertSeriesEquals(self, series1, series2):
        return self.assertSeriesEquals(series1, series2)
        
    def assertSeriesEqual(self, series1, series2):
        assert_series_equal(series1.series, series2.series, check_dtype=False)
        if len(series1.cout) != 0 and len(series2.cout) != 0:
            assert_series_equal(series1.cout, series2.cout, check_dtype=False)

class DatasetAssertions(SeriesAssertions):
    def assertDatasetEquals(self, dataset1, dataset2):
        return self.assertDatasetEquals(dataset1, dataset2)
        
    def assertDatasetEqual(self, dataset1, dataset2):
        for name, series in dataset1.dataset.items():
            self.assertTrue(name in dataset2.dataset)
            self.assertSeriesEqual(series, dataset2.dataset[name])
        for name, series in dataset2.dataset.items():
            self.assertTrue(name in dataset1.dataset)
            self.assertSeriesEqual(series, dataset1.dataset[name])

class ResultAssertions(DatasetAssertions, SeriesAssertions):
    def assertResultEquals(self, result1, result2):
        return self.assertResultEquals(result1, result2)
        
    def assertResultEqual(self, result1, result2):
        result1 = Result.lift(result1)
        result2 = Result.lift(result2)
        if result1.dataset is not None and result2.dataset is not None:
            self.assertDatasetEqual(result1.dataset, result2.dataset)
        self.assertEqual(result1.aggregations, result2.aggregations)

class WaveGenerator:
    def __init__(self):
        self.waves = []

    def add(self, frequency=60, amplitude=1, phase_shift=0):
        self.waves.append(WaveDescription(frequency, amplitude, phase_shift))
        return self

    def generate(self, sample_rate=10000, duration=1):
        result = None
        for wave_description in self.waves:
            wave = self.generate_single_wave(wave_description, sample_rate, duration)
            if result: result.add(wave)
            else: result = wave
        return result
        
    def generate_single_wave(self, wave_description, sample_rate, duration):
        times = np.arange(duration * sample_rate) / sample_rate
        signal = np.sin(2 * np.pi * wave_description.frequency * times + wave_description.phase_shift) * wave_description.amplitude
        return Wave(times, signal)

class Wave:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_times(self):
        now = datetime.now()
        return list(map(lambda n: now + timedelta(seconds=n), self.x))

    def get_signal(self):
        return self.y

    def to_series(self):
        return Series(self.y, self.get_times())

    def plot(self):
        import matplotlib.pyplot as plt
        plt.plot(self.x, self.y)
        plt.title('Wave')
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.grid(True, which='both')
        plt.axhline(y=0, color='k')
        plt.show()

    def plot_fft(self):
        import matplotlib.pyplot as plt
        ft = np.fft.fft(self.y)
        delta_time = self.x[1] - self.x[0]
        freq = np.fft.fftfreq(len(self.y), delta_time)

        plt.ylabel("Amplitude")
        plt.xlabel("Frequency [Hz]")
        plt.plot(freq, np.abs(ft))
        plt.show()    

    def add(self, other):
        self.y += other.y
        return self

class WaveDescription:
    def __init__(self, frequency, amplitude, phase_shift):
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase_shift = phase_shift

from datetime import datetime, timedelta

from .result import Result
from .series import Series

from pandas.testing import assert_series_equal
import numpy as np

class SeriesAssertions:
    def assertSeriesEquals(self, series1, series2):
        return self.assertSeriesEquals(series1, series2)
        
    def assertSeriesEqual(self, series1, series2):
        assert_series_equal(series1.series, series2.series)
        assert_series_equal(series1.cout, series2.cout)

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

class WaveformGenerator:
    def __init__(self):
        self.waveforms = []

    def add(self, frequency=60, amplitude=1):
        self.waveforms.append(WaveformDescription(frequency, amplitude))
        return self

    def generate(self, sample_rate=10000, duration=1):
        result = None
        for waveform_description in self.waveforms:
            waveform = self.generate_single_waveform(waveform_description, sample_rate, duration)
            if result: result.add(waveform)
            else: result = waveform
        return result
        
    def generate_single_waveform(self, waveform_description, sample_rate, duration):
        times = np.arange(duration * sample_rate) / sample_rate
        signal = np.sin(2 * np.pi * waveform_description.frequency * times) * waveform_description.amplitude
        return Waveform(times, signal)
        
        # sample_count = duration * sample_rate
        # x = np.arange(0, duration, 1/sample_rate)
        # xs = np.arange(sample_count)
        # y = np.sin(2 * np.pi * waveform_description.frequency * xs / sample_count) * waveform_description.amplitude
        # return Waveform(x, y)

class Waveform:
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

class WaveformDescription:
    def __init__(self, frequency, amplitude):
        self.frequency = frequency
        self.amplitude = amplitude


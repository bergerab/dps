from .result import Result

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



# Based off of: https://mindchasers.com/dev/python-harmonics
def generate_sine_wave(sample_rate=10000,
                       duration=1,
                       frequency=60):
    samples = duration * sample_rate
    x = np.arange(0, duration, 1/sample_rate)
    X = np.arange(samples)
    y = np.sin(2 * np.pi * frequency * X / samples)
    return x, y

# def generate_sine_wave(sample_rate=10000,
#                        duration=1,
#                        frequency=60,
#                        harmonics=0,
#                        harmonic_type='odd',
#                        shape='sine'):
#     f = frequency
    
#     if harmonic_type == 'even':
#         odd = 0
#         mult = 2
#     elif harmonic_type == 'odd':
#         odd = 1
#         mult = 2
#     else: # all
#         odd = 0
#         mult = 1

#     total_samples = sample_rate * duration
#     t = np.linspace(0, duration, num=total_samples)
#     y = np.zeros(total_samples)
    
#     # Compute and add fundamental with each harmonic
#     for i in range(int(harmonics)+1):
#         k = i * mult + odd # I added the +1 here (division by zero otherwise)
#         yh = factor(shape,k,i) * np.sin(2 * np.pi * k *  f * t)
#         y = y + yh

#     return t, y

# def factor(shape, k, i):
#     if shape == "triangle":
#         return (1/(k*k) * (-1)**i)
#     else:
#         return (1/k)

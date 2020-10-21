from .result import Result

from pandas.testing import assert_series_equal

class DatasetAssertions:
    def assertDatasetEquals(self, dataset1, dataset2):
        return self.assertDatasetEquals(dataset1, dataset2)
        
    def assertDatasetEqual(self, dataset1, dataset2):
        for name, series in dataset1.dataset.items():
            self.assertTrue(name in dataset2.dataset)
            self.assertSeriesEqual(series, dataset2.dataset[name])
        for name, series in dataset2.dataset.items():
            self.assertTrue(name in dataset1.dataset)
            self.assertSeriesEqual(series, dataset1.dataset[name])

class SeriesAssertions:
    def assertSeriesEquals(self, series1, series2):
        return self.assertSeriesEquals(series1, series2)
        
    def assertSeriesEqual(self, series1, series2):
        assert_series_equal(series1.series, series2.series)
        assert_series_equal(series1.cout, series2.cout)

class ResultAssertions(DatasetAssertions, SeriesAssertions):
    def assertResultEquals(self, result1, result2):
        return self.assertResultEquals(result1, result2)
        
    def assertResultEqual(self, result1, result2):
        result1 = Result.lift(result1)
        result2 = Result.lift(result2)
        if result1.dataset is not None and result2.dataset is not None:
            self.assertDatasetEqual(result1.dataset, result2.dataset)
        self.assertEqual(result1.aggregations, result2.aggregations)

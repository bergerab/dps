from itertools import chain
import pandas as pd

from .stream import SeriesStream
from .aggregation import \
    MaxAggregation, \
    MinAggregation, \
    AverageAggregation

from pandas.testing import assert_series_equal

class Dataset:
    def __init__(self, dataset=None):
        self.dataset = {} if dataset is None else dataset
        
    def add(self, name, series):
        self.dataset[name] = series

    def select(self, names):
        dataset = {}
        for name in names:
            dataset[name] = self.dataset[name]
        return Dataset(dataset)

    def merge(self, other):
        dataset = {}
        for name, value in chain(self.dataset.items(), other.dataset.items()):
            if name in dataset:
                dataset[name] = dataset[name].concat(value)
            else:
                dataset[name] = value
        return Dataset(dataset)

    def rename(self, mappings):
        dataset = {}
        for old_name, new_name in mappings.items():
            dataset[new_name] = self.dataset[old_name]
        return Dataset(dataset)

    def has(self, name):
        return name in self.dataset

    def get(self, name):
        return self.dataset[name]

    def __eq__(self, other):
        for name, series in self.dataset.items():
            if name not in other.dataset:
                return False
            if not series.equals(other.dataset[name]):
                return False
        for name, series in other.dataset.items():
            if name not in self.dataset:
                return False
            if not series.equals(self.dataset[name]):
                return False
        return True

    def __repr__(self):
        return repr(self.dataset)

class Series:
    '''
    A wrapper around pandas Series.
    '''
    def __init__(self, data=None, times=None, cin=None, cout=None):
        # Cout is the "carry-out" from the previous windowed operation
        # It is only when sequencing many series computations together to do
        # stream processing.
        self.cout = pd.Series([], dtype='float64') if cout is None else cout
        
        if data is None or len(data) == 0:
            series = pd.Series(data, dtype='float64')
        else:
            series = pd.Series(data, index=times)
        self.series = pd.concat([cin, series]) if cin is not None else series

    def __iter__(self):
        return self.series.__iter__()

    def __len__(self):
        return self.series.__len__()

    def __add__(self, other):
        return Series.binop(self, other, lambda x, y: x + y)
    
    def __radd__(self, other):
        return Series.binop(self, other, lambda x, y: x + y)

    def __sub__(self, other):
        return Series.binop(self, other, lambda x, y: x - y)
    
    def __rsub__(self, other):
        return Series.binop(self, other, lambda x, y: y - x)

    def __mul__(self, other):
        return Series.binop(self, other, lambda x, y: x * y)

    def __rmul__(self, other):
        return Series.binop(self, other, lambda x, y: y * x)        

    def __truediv__(self, other):
        return Series.binop(self, other, lambda x, y: x / y)                

    def __rtruediv__(self, other):
        return Series.binop(self, other, lambda x, y: y / x)

    def __floordiv__(self, other):
        return Series.binop(self, other, lambda x, y: x // y)

    def __rfloordiv__(self, other):
        return Series.binop(self, other, lambda x, y: y // x)        

    def __neg__(self):
        return -self.series

    def __gt__(self, other):
        return Series.binop(self, other, lambda x, y: x > y)

    def __lt__(self, other):
        return Series.binop(self, other, lambda x, y: x < y)

    def __ge__(self, other):
        return Series.binop(self, other, lambda x, y: x >= y)

    def __le__(self, other):
        return Series.binop(self, other, lambda x, y: x <= y)

    def __eq__(self, other):
        return Series.binop(self, other, lambda x, y: x == y)

    def __ne__(self, other):
        return Series.binop(self, other, lambda x, y: x != y)

    def _and(self, other):
        return Series.binop(self, other, lambda x, y: x & y)

    def _or(self, other):
        return Series.binop(self, other, lambda x, y: x | y)

    def equals(self, other):
        return len(self.series) == len(other.series) and \
            self.series.equals(other.series) \
            and self.cout.equals(other.cout)

    def concat(self, other):
        return Series(pd.concat([self.series, other.series]))

    def window(self, duration):
        windows = []
        stream = SeriesStream(self.series)

        start_time, _ = stream.get()
        stream.unget()
        end_time = start_time + duration

        values = []
        times = []
        while stream.has_values():
            time, value = stream.get()
            if time >= end_time:
                stream.unget()
                windows.append(pd.Series(values, index=times))
                start_time = time
                end_time = start_time + duration
                values = []
                times = []
            else:
                values.append(value)
                times.append(time)
        return Series(windows, cout=pd.Series(values, index=times))

    def when(self, body, orelse):
        '''
        Maps True values in self to body values and False values to orelse_series values.
        Requires that test_series, body, and orelse times match exactly, or else will produce incorrect results.
        This looks like an if expression, but don't be fooled, this computes both body and orelse regardless 
        if self is all False or all True
        '''
        series = []
        for i in range(len(self.series)):
            if self.series[i]:
                if isinstance(body, Series):
                    value = body.series[i]
                else:
                    value = body
            else:
                if isinstance(orelse, Series):
                    value = orelse.series[i]
                else:
                    value = orelse
            series.append(value)
        return Series.create_with_series(pd.Series(series, index=self.series.index))

    def average_aggregation(self):
        sum = 0
        count = 0
        for x in self:
            sum += x
            count += 1
        return AverageAggregation.from_sum_and_count(self, sum, count)

    def aggregate(self, f):
        values = []
        times = []
        for series in self.series:
            values.append(f(series))
            times.append(series.index[0])
        return Series(values,
                      times,
                      cout=self.cout)

    def average(self):
        return self.aggregate(lambda x: x.mean())

    def min_aggregation(self):
        local_min = None
        for x in self:
            if local_min is None:
                local_min = x
            else:
                local_min = min(x, local_min)
        return MinAggregation(self, local_min)

    def min(self):
        return self.aggregate(lambda x: x.min())

    def max_aggregation(self):
        local_max = None
        for x in self:
            if local_max is None:
                local_max = x
            else:
                local_max = max(x, local_max)
        return MaxAggregation(self, local_max)

    def max(self):
        return self.aggregate(lambda x: x.max())

    def is_windowed(self):
        if len(self.series) == 0:
            return False
        if isinstance(self.series[0], pd.Series):
            return True
        return False

    def to_dataset(self, name):
        return Dataset({
            name: self,
        })

    def windows_to_list(self):
        return list(map(lambda series: list(series), list(self.series)))

    @staticmethod
    def binop(series, other, f):
        if isinstance(other, Series):
            cout = None
            series_is_windowed = series.is_windowed()
            other_is_windowed = other.is_windowed()
            if series_is_windowed and other_is_windowed:
                raise Exception('You cannot perform binary operations on two windowed series.')
            elif series_is_windowed:
                cout = series.cout
            elif other_is_windowed:
                cout = other.cout
            return Series(f(series.series, other.series), cout=cout)
        else:
            return Series(f(series.series, other), cout=series.cout)

    @staticmethod
    def create_with_series(series, cout=None):
        s = Series(cout=cout)
        s.series = series
        return s

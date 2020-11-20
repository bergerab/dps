import pandas as pd

from .dataset import *
from .stream import SeriesStream
from .aggregation import \
    Aggregation, \
    MaxAggregation, \
    MinAggregation, \
    AverageAggregation

class Series:
    '''
    A wrapper around pandas Series.
    '''
    def __init__(self, data=None, times=None, cin=None, cout=None, cout_enabled=False):
        # Cout is the "carry-out" from the previous windowed operation
        # It is only when sequencing many series computations together to do
        # stream processing.
        
        # If `cout_enabled` is true, windowed computations who's final window is not complete
        # will still be put into a window (instead of being added to `cout` to be computed when more data comes).
        
        self.cout = pd.Series([], dtype='float64') if cout is None else cout

        # `pd.dropna` drops any null values. This is important because some computations may
        # enter a null value as an indication to skip a computation (it will be skipped via
        # dropping the data).
        if data is None or len(data) == 0:
            series = pd.Series(data, dtype='float64').dropna()
        else:
            series = pd.Series(data, index=times).dropna()
        self.series = pd.concat([cin, series]) if cin is not None else series
        self.cout_enabled = cout_enabled

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
        if len(self.series) == 0:
            return Series([])
        
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
        if not self.cout_enabled:
            windows.append(pd.Series(values, index=times))
            values = []
            times = []
        return Series(windows, cout=pd.Series(values, index=times) if values and times else None)

    def when(self, body, orelse):
        '''
        Maps True values in self to body values and False values to orelse_series values.
        Requires that test_series, body, and orelse times match exactly, or else will produce incorrect results.
        This looks like an if expression, but don't be fooled, this computes both body and orelse regardless 
        if self is all False or all True
        '''
        series = []
        indices = []
        for i in range(len(self.series)):
            if self.series[i]:
                if isinstance(body, Series):
                    value = body.series[i]
                    indices.append(self.series.index[i])
                # For aggregations, the sizes of the series may be different
                # so we have to locate the closest time to the sample to use.
                elif isinstance(body, Aggregation):
                    if len(body.series.series) == 0:
                        continue
                    index_value = self.series.index[i]
                    index = body.series.series.index.get_loc(index_value, method='nearest')
                    value = body.series.series[index]
                    indices.append(self.series.index[i])                        
                else:
                    value = body
            else:
                if isinstance(orelse, Series):
                    value = orelse.series[i]
                    indices.append(self.series.index[i])
                elif isinstance(orelse, Aggregation):
                    if len(orelse.series.series) == 0:
                        continue
                    value = orelse.series.series[orelse.series.series.index.get_loc(self.series.index[i], method='nearest')]
                    indices.append(self.series.index[i])                                            
                else:
                    value = orelse
                    indices.append(self.series.index[i])                        
            series.append(value)
        return Series.create_with_series(pd.Series(series, index=indices))

    def average_aggregation(self):
        xs = self.series.sum()
        return AverageAggregation.from_sum_and_count(self,
                                                     xs,
                                                     self.series.size)

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
        if isinstance(self.series.iloc[0], pd.Series):
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
        elif isinstance(series, Aggregation):
            return Series.binop(series.series, other, f)
        elif isinstance(other, Aggregation):
            return Series.binop(series, other.series, f)
        else:
            return Series(f(series.series, other), cout=series.cout)

    @staticmethod
    def create_with_series(series, cout=None):
        s = Series(cout=cout)
        s.series = series.dropna()
        return s

from datetime import datetime, timedelta
from pandas.api.types import is_datetime64_any_dtype as is_datetime

import numpy as np

class Datapoint:
    '''
    A value with an absolute time
    '''
    def __init__(self, value, time):
        self.value = value
        self.time = time

class ListStream:
    def __init__(self, xs):
        self.xs = xs
        self.i = 0
        self.lookback = 0

    def get(self):
        value = self.xs[self.i]
        self.i += 1
        return value
        
    def unget(self):
        self.i -= 1

    def has_values(self):
        return self.i < len(self.xs)

    def save(self):
        self.lookback = self.i

    def restore(self):
        self.i = self.lookback
        
class DataSeries:
    def __init__(self, datapoints=None):
        self.datapoints = [] if not datapoints else datapoints

    def add(self, value, time):
        '''
        Adds a value/time pair to the DataSeries (must be added in monotonically increasing order).
        '''
        self.datapoints.append(Datapoint(value, time))

    def map(self, f):
        '''
        Maps a function over the values of the DataSeries.
        '''
        ds = DataSeries()
        for datapoint in self.datapoints:
            ds.add(f(datapoint.value), datapoint.time)
        return ds

    def to_list(self):
        '''
        Returns all values from the DataSeries (discards the time information).
        '''
        return list(map(lambda x: x.value, self.datapoints))

    def get_times(self):
        return list(map(lambda x: x.time, self.datapoints))

    @staticmethod
    def from_list(xs, start_time=datetime.now(), delta_time=timedelta(seconds=1)):
        '''
        Creates a DataSeries from a list of values, a `start_time` which indicates when the 
        first sample was taken, and a `delta_time` which indicates how much time passes between
        each sample in the list.
        '''
        ds = DataSeries()
        for i, x in enumerate(xs):
            ds.add(x, start_time + (delta_time * i))
        return ds

    @staticmethod
    def from_df(df, column, time_column='Time'):
        '''
        Create a DataSeries from a Pandas DataFrame column.
        '''
        if column not in df:
            raise Exception(f'DataFrame column "{column}" does not exist.')
        if time_column not in df:
            raise Exception(f'DataFrame time column "{time_column}" does not exist.')
            
        ds = DataSeries()
        for i, row in df.iterrows():
            ds.add(row[column], row[time_column])
        return ds

    def add_datapoint(self, datapoint):
        self.datapoints.append(datapoint)

    def start_time(self):
        return self.datapoints[0].time

    def end_time(self):
        return self.datapoints[-1].time

    def time_window(self, duration):
        '''
        Returns a DataSeries of DataSeries where each DataSeries is a window

        duration is how long each window should represent (as a datetime.timedelta object)
        '''
        windows = DataSeries()
        stream = ListStream(self.datapoints)
        
        def add_window():
            if not stream.has_values(): return
            window = DataSeries()                        
            window.add_datapoint(stream.get())
            while stream.has_values():
                datapoint = stream.get()
                if datapoint.time - window.start_time() >= duration:
                    stream.unget()
                    break
                else:
                    window.add_datapoint(datapoint)
            # windows their first value's time as their start_time
            # this could be defined differently, but it doesn't matter
            windows.add(window, window.start_time())
        
        while stream.has_values():
            add_window()
            
        return windows

    def when(self, body, orelse):
        '''
        Maps True values in self to body values and False values to orelse_series values.
        Requires that test_series, body, and orelse times match exactly, or else will produce incorrect results.

        This looks like an if expression, but don't be fooled, this computes both body and orelse regardless 
        if self is all False or all True
        '''
        ds = DataSeries()
        for i in range(len(self.datapoints)):
            dp = self.datapoints[i]
            if dp.value:
                if isinstance(body, DataSeries):
                    value = body.datapoints[i].value
                else:
                    value = body
            else:
                if isinstance(orelse, DataSeries):
                    value = orelse.datapoints[i].value
                else:
                    value = orelse
            ds.add(value, dp.time)
        return ds

    def thd(self, base_harmonic):
        fft_vals = np.absolute(np.fft.fft(list(self)))

        # Look at twice the amount just in case we miss the base harmonic
        fund_freq, fund_freq_idx = max([(v,i) for i,v in enumerate(fft_vals[:2*base_harmonic])])

        sum = 0        
        harmonic = fund_freq_idx + base_harmonic
        offset = int(base_harmonic/2)

        while harmonic < len(fft_vals)/2:
            peak = np.max(fft_vals[harmonic - offset : harmonic + offset])
            sum += peak * peak
            harmonic += base_harmonic

        thd = np.sqrt(sum) / fund_freq

        return thd;

    def windows_to_list(self):
        '''
        Takes a nested DataSeries of DataSeries and returns just a List of Lists
        '''
        return list(map(lambda x: list(x), list(self)))

    def __len__(self):
        return len(self.datapoints)

    def __iter__(self):
        for datapoint in self.datapoints:
            yield datapoint.value

    def __add__(self, other):
        return self.pointwise(other, lambda x, y: x + y)
    def __radd__(self, other):
        return self + other
    def __sub__(self, other):
        return self.pointwise(other, lambda x, y: x - y)
    def __rsub__(self, other):
        return self.pointwise(other, lambda x, y: y - x)        
    def __mul__(self, other):
        return self.pointwise(other, lambda x, y: x * y)
    def __rmul__(self, other):
        return self * other
    def __truediv__(self, other):
        return self.pointwise(other, lambda x, y: x / y)
    def __rtruediv__(self, other):
        return self.pointwise(other, lambda x, y: y / x)        
    def __floordiv__(self, other):
        return self.pointwise(other, lambda x, y: x // y)
    def __rfloordiv__(self, other):
        return self.pointwise(other, lambda x, y: y // x)        

    def __neg__(self):
        return self.map(lambda x: -x)

    def __gt__(self, other):
        return self.pointwise(other, lambda x, y: x > y)
    def __lt__(self, other):
        return self.pointwise(other, lambda x, y: x < y)
    def __ge__(self, other):
        return self.pointwise(other, lambda x, y: x >= y)
    def __le__(self, other):
        return self.pointwise(other, lambda x, y: x <= y)
    def __eq__(self, other):
        return self.pointwise(other, lambda x, y: x == y)
    def __neq__(self, other):
        return self.pointwise(other, lambda x, y: x != y)

    def _and(self, other):
        return self.pointwise(other, lambda x, y: x and y)
    def _or(self, other):
        return self.pointwise(other, lambda x, y: x or y)

    def pointwise(self, other, f):
        ds = DataSeries()
        if isinstance(other, DataSeries):        
            for datapoint1, datapoint2 in zip(self.datapoints, other.datapoints):
                ds.add(f(datapoint1.value, datapoint2.value), datapoint1.time)
        else:
            for datapoint in self.datapoints:
                ds.add(f(datapoint.value, other), datapoint.time)
        return ds

    def average(self):
        return self.aggregate(lambda ds: sum(ds)/len(ds))
    def avg(self): return self.average()
    def mean(self): return self.average()

    def is_windowed(self):
        '''
        Is this series a nested DataSeries (some windowing has been applied)
        '''
        return not self.datapoints or isinstance(self.datapoints[0].value, DataSeries)

    def aggregate(self, f):
        if not self.is_windowed(): raise Exception('Aggregations can only be made on windowed DataSeries.')
        agg = DataSeries()
        for dp in self.datapoints:
            value = f(dp.value)
            for sub_dp in dp.value.datapoints:
                agg.add(value, sub_dp.time)
        return agg

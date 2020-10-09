from datetime import datetime, timedelta
from pandas.api.types import is_datetime64_any_dtype as is_datetime

from .aggregation import *

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
        return self.aggregate(lambda ds: ds.thd_series(base_harmonic))

    def thd_series(self, base_harmonic):
        '''
        Runs a THD computation on this series (assumes series is not windowed).
        '''
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

    def thd2(self, base_harmonic,fs):
        return self.aggregate(lambda ds: ds.thd_series(base_harmonic))

    def thd2_series(self, base_harmonic,fs):
        fv = np.fft.fft(list(self))
        f_abs = np.abs(fv)
        N = len(v)
        f = np.linspace(0, 0.5 * fs, N // 2)

        all_freqs = np.argsort(-f_abs[:N // 2])
        all_peaks = f_abs[:N // 2]
        fund_freq = f[all_freqs[0]]
        v_rms_0 = all_peaks[all_freqs[0]]
        offset = 10 * abs((fund_freq - base_harmonic) / base_harmonic)

        # Identify harmonics peaks within in 25% range of harmonics
        harmonic = fund_freq + base_harmonic
        v_rms_harmonics = 0
        while harmonic < f[-1]:
            ind = [indx for indx, x in enumerate(f) if x >= harmonic * (1 - offset) and x < harmonic * (1 + offset)]
            ind = ind[np.argmax(all_peaks[ind])]
            harmonic = f[ind]
            peak = np.max(all_peaks[ind])
            v_rms_harmonics = v_rms_harmonics + (peak * peak)
            harmonic = harmonic + base_harmonic

        thd2 = np.sqrt(v_rms_harmonics) / v_rms_0
        return thd2

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

    def average_aggregation(self):
        sum = 0
        count = 0
        for x in self:
            sum += x
            count += 1
        return AverageAggregation.from_sum_and_count(sum, count)

    def average(self):
        return self.aggregate(lambda ds: sum(ds)/len(ds))

    def avg(self): return self.average()
    
    def mean(self): return self.average()

    def min_aggregation(self):
        local_min = None
        for x in self:
            if local_min is None:
                local_min = x
            else:
                local_min = min(x, local_min)
        return MinAggregation(local_min)

    def min(self):
        return self.aggregate(lambda ds: min(ds))

    def max_aggregation(self):
        local_max = None
        for x in self:
            if local_max is None:
                local_max = x
            else:
                local_max = max(x, local_max)
        return MaxAggregation(local_max)

    def max(self):
        return self.aggregate(lambda ds: max(ds))

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

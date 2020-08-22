from datetime import datetime, timedelta

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
        self.datapoints.append(Datapoint(value, time))

    def map(self, f):
        ds = DataSeries()
        for datapoint in self.datapoints:
            ds.add(f(datapoint.value), datapoint.time)
        return ds

    def to_list(self):
        return list(map(lambda x: x.value, self.datapoints))

    @staticmethod
    def from_list(xs, start_time=datetime.now(), delta_time=timedelta(seconds=1)):
        ds = DataSeries()
        for i, x in enumerate(xs):
            ds.add(x, start_time + (delta_time * i))
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

    def when(self, body_series, orelse_series):
        '''
        Maps True values in self to body_series values and False values to orelse_series values.
        Requires that test_series, body_series, and orelse_series times match exactly, or else will produce incorrect results.

        This looks like an if expression, but don't be fooled, this computes both body_series and orelse_series regardless 
        if self is all False or all True
        '''
        ds = DataSeries()
        for i in range(len(self.datapoints)):
            dp = self.datapoints[i]
            if dp.value:
                ds.add(body_series.datapoints[i].value, dp.time)
            else:
                ds.add(orelse_series.datapoints[i].value, dp.time)
        return ds

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
    def __sub__(self, other):
        return self.pointwise(other, lambda x, y: x - y)
    def __mul__(self, other):
        return self.pointwise(other, lambda x, y: x * y)
    def __truediv__(self, other):
        return self.pointwise(other, lambda x, y: x / y)
    def __floordiv__(self, other):
        return self.pointwise(other, lambda x, y: x // y)

    def __gt__(self, other):
        return self.pointwise(other, lambda x, y: x > y)
    def __lt__(self, other):
        return self.pointwise(other, lambda x, y: x < y)
    def __gte__(self, other):
        return self.pointwise(other, lambda x, y: x >= y)
    def __lte__(self, other):
        return self.pointwise(other, lambda x, y: x <= y)
    def __eq__(self, other):
        return self.pointwise(other, lambda x, y: x == y)
    def __neq__(self, other):
        return self.pointwise(other, lambda x, y: x != y)

    def pointwise(self, other, f):
        ds = DataSeries()
        for datapoint1, datapoint2 in zip(self.datapoints, other.datapoints):
            ds.add(f(datapoint1.value, datapoint2.value), datapoint1.time)
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
            agg.add(f(dp.value), dp.time)
        return agg

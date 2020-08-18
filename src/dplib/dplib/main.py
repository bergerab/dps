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

    def get(self):
        value = self.xs[self.i]
        self.i += 1
        return value
        
    def unget(self):
        self.i -= 1

    def has_values(self):
        return self.i < len(self.xs)
        
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

    def time_window(self, duration, stride=timedelta(seconds=1)):
        '''
        Returns a DataSeries of DataSeries where each DataSeries is a window

        duration is how long each window should represent (as a datetime.timedelta object)
        stride is how long to skip between each window (datetime.timedelta object)
        '''
        windows = DataSeries()
        stream = ListStream(self.datapoints)
        
        def add_window():
            if not stream.has_values(): return
            window = DataSeries()                        
            window.add_datapoint(stream.get())
            while stream.has_values():
                datapoint = stream.get()
                if datapoint.time - window.start_time() > duration:
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

class DataSet:
    def __init__(self, data_map):
        self.data_map = data_map

import re

import functions as funcs
from main import DataSeries


time_pattern = re.compile('(\d+)(ms|s|m|h)')
'''
Times are represented as strings of the form:
200ms -> 200 milliseconds
10s   -> 10 seconds
3m    -> 3 minutes
4h    -> 4 hours
'''

unit_map = {
    'ms': 'milliseconds',
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
}
'''
A mapping from shorthand names to the names timedelta uses as keywords.
'''

def parse_time(id):
    '''
    Parses a string into a timedelta value
    '''
    result = time_pattern.search(id)
    if not result: return None
    magnitude, units = result.groups()
    return timedelta(**{ unit_map[units]: int(magnitude) })
        

if __name__ == '__main__':
    # Test creating DataSeries from list
    time = datetime.now()        
    ds = DataSeries.from_list([1,2,3,4], start_time=time, delta_time=timedelta(seconds=2))
    assert ds.start_time() == time
    assert ds.end_time() == time + timedelta(seconds=2)*3
    assert ds.to_list() == [1,2,3,4]

    # Test point-wise computations
    ds1 = DataSeries.from_list([1,2])
    ds2 = DataSeries.from_list([3,4])
    ds3 = ds1 + ds2
    assert (ds1 + ds2).to_list() == [1+3, 2+4]
    assert (ds1 - ds2).to_list() == [1-3, 2-4]
    assert (ds1 * ds2).to_list() == [1*3, 2*4]
    assert (ds1 / ds2).to_list() == [1/3, 2/4]
    assert (ds1 // ds2).to_list() == [1//3, 2//4]
    
    # Test windowed computations
    ds = DataSeries()
    ds.add(1, time)
    ds.add(1.3, time + timedelta(seconds=0.1))
    ds.add(2, time + timedelta(seconds=1.1))
    dss = ds.time_window(timedelta(seconds=1))
    assert dss.average().to_list()[0] == sum([1, 1.3])/2
    assert dss.average().to_list()[1] == 2
    assert len(dss.average().to_list()) == 2


'''
    functions = { # TODO: pass this in
        '+': funcs.add,
        '-': funcs.sub,
        '*': funcs.mul,
        '/': funcs.div,
        '//': funcs.floordiv,                                
        'AVERAGE': funcs.average,
        'WINDOW': funcs.window,
        'THD': lambda args: 3,
    }
'''

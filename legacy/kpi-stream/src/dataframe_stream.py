import pandas as pd
import numpy as np 
import numpy
import matplotlib.pyplot as plt

# Stream from a generator function
class Stream:
    def __init__(self, generatorFun):
        self.generatorFun = generatorFun
        
    def tumbling_window(self, window_size):
        return self.hopping_window(window_size, window_size)

    # make windows from generators -- less efficient than windows from data frame
    def hopping_window(self, window_size, hop_size):
        def next(generator, n):
            i = 0
            ret = []
            while(i < n):
                ret.append(generator.__next__())
                i = i + 1
            return ret

        def gen_tumbling():
            generator = self.generatorFun()

            try:
                while True:
                    yield next(generator, window_size)
            except StopIteration: 
                return

        def gen_small_hop():
            generator = self.generatorFun()

            try:
                data_window = next(generator, window_size)
                yield data_window

                while True:
                    data_window = data_window[hop_size:] + next(generator, hop_size)
                    yield data_window
            except StopIteration:
                 return

        def gen_big_hop():
            generator = self.generatorFun()

            try:
                while True:
                    yield next(generator, hop_size)[:window_size]
            except StopIteration:
                return

        if(window_size == hop_size):
            ret = gen_tumbling
        elif(window_size < hop_size):
            ret = gen_big_hop
        else:
            ret = gen_small_hop

        return Stream(ret)

    # self: Stream 'a
    # f: 'a -> b
    # return: Stream 'b
    def map(self, f):
        def gen():
            for x in self.generatorFun():
                yield f(x) 
        return Stream(gen)

    # self: Stream ['a]
    # f: 'a -> 'b
    # return: Stream ['b]
    def mapAll(self, f):
        return self.map(lambda x: list(map(f, x)))

    # self: Stream ['a]
    # f: ('a, 'a, ...) -> 'b
    # return: Stream 'b
    def mapSpread(self, f):
        return self.map(lambda x: f(*x))

    # preserve the first column (assuming it is time)
    #   while mapping the rest to f (by spreading the list)
    # f: takes a list of arguments and returns a result list
    def mapWithTime(self, f):
        def gen():
            generator = self.generatorFun()
            x = generator.__next__()
            r = f(*x[1:])

            if(isinstance(r, list)):
                yield [x[0]] + r
                for x in generator:
                    yield [x[0]] + f(*x[1:]) 
            else:
                yield [x[0], r]
                for x in generator:
                    yield [x[0], f(*x[1:])] 

        return Stream(gen)

    
    # self: Stream 'b
    # f: ('a, 'b) -> 'a, init: 'a
    # return: Stream 'a
    def scan(self, f, init):
        def gen():
            ret = init
            for x in self.generatorFun():
                ret = f(ret, x)
                yield ret

        return Stream(gen)

    # f: ('a, 'b) -> 'a, init: 'a
    # return: 'a
    def reduce(self, f, init):
        ret = init
        for x in self.generatorFun():
            ret = f(ret, x)
        return ret

    # integrate (or sum) self over time
    # self: Stream [Time, 'a]
    # return: Stream [Time, 'a * dt]
    def integrate(self, init=[0,0]):
        def f(t1_sofar, t2_v):
            t1, sofar = t1_sofar
            t2, v = t2_v
            return [t2, sofar + v*(t2-t1)]

        return self.scan(f, init)


    # this: Stream 'a, that: Stream 'b
    # return: Stream ('a, 'b)
    def zip(self, that):

        def gen():
            that_generator = that.generatorFun()
            
            for x in self.generatorFun():
                yield [x, that_generator.__next__()]

        return Stream(gen)

    # this: Stream 'a or Stream ['a], that: Stream 'a or Stream ['a]
    # return: Stream ['a]
    def merge(self, that):
        def gen():
            this_generator = self.generatorFun()
            that_generator = that.generatorFun()
            x = this_generator.__next__()
            y = that_generator.__next__()

            try: 
                if isinstance(x, list):
                    if isinstance(y, list):
                        yield x + y
                        for x in this_generator:
                            yield x + that_generator.__next__()
                    else:
                        yield x + [y]
                        for x in this_generator:
                            yield x + [that_generator.__next__()]
                else:
                    if isinstance(y, list):
                        yield [x] + y
                        for x in this_generator:
                            yield [x] + that_generator.__next__()
                    else:
                        yield [x,y]
                        for x in this_generator:
                            yield [x, that_generator.__next__()]
            except: 
                StopIteration

        return Stream(gen)

    # assume 'that' has a time column, which is excluded from the merged stream 
    def mergeWithTime(self, that):
        def gen():
            that_generator = that.generatorFun()

            for x in self.generatorFun():
                yield x + that_generator.__next__()[1:]

        return Stream(gen)

    # assume 'that' has a time column, which is excluded from the merged stream
    # TODO: this is a hack
    def interpolateMergeWithTime(self, that):
        def gen():
            for x in self.generatorFun():
                yield x + that.generatorFun().__next__()[1:]

        return Stream(gen)

    # names: [String] column names
    # return a DataFrame with rows concatenated from the stream
    def concat(self, names=None):
        data = []
        for x in self.generatorFun():
            data.append(x)

        if(names == None):
            ret = pd.DataFrame(data)
        else:
            ret = pd.DataFrame(data, columns=names)
        return ret

    # return: last value of this stream
    def last(self):
        for x in self.generatorFun():
            ret = x
        return ret

    # for each value x of this stream, call f(x)
    def subscribe(self, f):
        for x in self.generatorFun():
            f(x)

    # self: Stream 'a
    # f: 'a -> Bool
    # return: Stream 'a
    def filter(self, f):
        def gen():
            for x in self.generatorFun():
                if(f(x)):
                    yield x
        return Stream(gen)

    def to_signal(self, names):
        return SignalStream(self.generatorFun, names)

    def print(self): print(self.concat())
    
# Make data windows from lists
class Window:
    def __init__(self, data):
        self.data = data

    # generator of non-overlapping window of fixed size
    # data: input data array, size: window size, return: an iterator of arrays of 'size' length 
    def tumbling(self, window_size=1):
        return self.hopping(window_size, window_size)

    def hopping(self, window_size=1, hop_size=1):
        length = len(self.data)

        for i in range(0, length, hop_size):
            yield self.data[i:min(i + window_size, length)]


# Stream from the rows of a DataFrame with more efficient windowing/concat mehod
class DataFrameStream(Stream):
    def __init__(self, rows, names):
        self.rows = rows
        self.names = names

        def gen():
            for x in rows:
                yield x

        Stream.__init__(self, gen)

    def hopping_window(self, window_size, hop_size):
        return Stream(lambda: Window(self.rows).hopping(window_size, hop_size)) 

    # names: [String] column names
    # return this data as DataFrame with new column names
    def concat(self, names=None):
        if(names == None):
            ret = pd.DataFrame(self.rows)
        else:
            ret = pd.DataFrame(self.rows, columns=names)
        return ret

    def to_signal(self, names=None):
        if(names == None):
            names = self.names
        return super().to_signal(names)

# A data stream with time as the first column
# names: column names for stream data
class SignalStream(Stream):
    def __init__(self, generatorFun, names):
        self.names = names
        self.df = None
        Stream.__init__(self, generatorFun)

    def concat(self, names=None):
        if(self.df is None):
            if(names == None): 
                names = self.names
            self.df = super().concat(self.names)

        return self.df

    def mapWithTime(self, f):
        return SignalStream(super().mapWithTime(f).generatorFun, self.names)


    def plot(self, ylim=None):
        yNames = self.names[1] if len(self.names) == 2 else self.names[1:]
        self.concat().plot(x=self.names[0], y=yNames)
        if not (ylim is None):
            plt.ylim(ylim)
        plt.show()

    def to_csv(self, fileName):
        self.concat().to_csv(fileName, index=False, sep=',')

    def to_df(self):
        return self.concat()

    # generate a signal sample for every 'dt' seconds
    # dt: time delta between samples. Each sample value is averaged over dt
    def sample(self, dt):
        def gen():
            generator = self.generatorFun()
            x = generator.__next__()
            t0 = x[0] 
            dataList = x[1:]
            accumulatorList = list(map(lambda x:[x], dataList))

            for x in generator:
                t = x[0]
                dataList = x[1:]

                if((t - t0) < dt):
                    for accumulator, data in zip(accumulatorList, dataList): 
                        accumulator.append(data)
                else:
                    yield [t0] + list(map(lambda x: sum(x)/len(x), accumulatorList))
                    t0 = t
                    accumulatorList = list(map(lambda x:[x], dataList))

        return SignalStream(gen, self.names)

    # animate this stream 
    # dt: duration between each sample 
    def stream_plot(self, dt, ylim=None):
        plt.ion()

        t = []
        y = list(map(lambda _:[], self.names))

        def plot(x):
            nonlocal t
            nonlocal y

            plt.clf()
            if(ylim != None): plt.ylim(ylim)

            t.append(x[0])
            for yi, xi, name in zip(y, x[1:], self.names[1:]):
                yi.append(xi)
                plt.plot(t, yi, label=name)

            plt.legend()
            plt.draw()
            plt.pause(dt)

        self.subscribe(plot)
        plt.show(block=True)

    def window_plot(self, dt, window_size, hop_size=1, ylim=None):
        plt.ion()

        def plot(x):
            plt.clf()
            if(ylim != None): plt.ylim(ylim)
            for yi, name in zip(x[1:], self.names[1:]):
                plt.plot(x[0], yi, label=name)

            plt.legend()
            plt.draw()
            plt.pause(dt)

        self.hopping_window(window_size, hop_size).map(lambda x: np.transpose(x)) \
                .subscribe(plot)
        plt.show(block=True)


# main

# csvFileName = '..\examples\power_electronics_inverter\Power_Electronics_Inverter_Model.csv'
# header = ['Time', 'Ia','Ib', 'Ic', 'Va', 'Vb', 'Vc', 'P_losses', 'THD_Ia', 'THD_Ib', 'THD_Ic', 'THD_Va', 'THD_Vb', 'THD_Vc', 'Idc', 'Pin_dc', 'Vdc']   

# Source(csvFileName, header, 20).proj('Time').hopping_window(10, 5).subscribe(lambda x: print(x))



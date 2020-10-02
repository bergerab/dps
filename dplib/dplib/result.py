import pandas as pd

from pandas._testing import assert_frame_equal

class ResultAssertions:
    def assertResultEqual(self, other):
        self.assertEquals(type(self), type(other))
        assert_frame_equal(self.df, other.df)
        self.assertEquals(self.assertions, other.assertions)

class Result:
    def __init__(self, df=None, aggregations=None):
        self.df = pd.DataFrame() if df is None else df 
        self.aggregations = {} if aggregations is None else aggregations

    def merge(self, other):
        aggregations = {}
        for key in self.aggregations:
            aggregations[key] = self.aggregations[key]
        for key in other.aggregations:
            aggregations[key] = other.aggregations[key]
        return Result(self.df.join(other.df),
                      aggregations)

    def equals(self, other):
        return self.df.equals(other.df) and \
               self.aggregations == other.aggregations

    @staticmethod
    def lift(x):
        if isinstance(x, pd.DataFrame):
            return Result(x, {})
        elif isinstance(x, dict):
            return Result(pd.DataFrame(), x)
        elif isinstance(x, Result):
            return x
        raise Exception(f'Invalid type to lift into a Result type {type(x)}.')

class AggregationCache:
    def __init__(self):
        self.cache = []
        self.precache = []
    
    def add(self, x):
        self.precache.append(x)

    def commit(self):
        self.cache = self.precache
        self.precache = []

    def pop(self):
        return self.cache.pop()

    def is_empty(self):
        return bool(self.cache)

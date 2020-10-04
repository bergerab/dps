import pandas as pd

from pandas._testing import assert_frame_equal

class ResultAssertions:
    def assertResultEquals(self, result1, result2):
        return self.assertResultEquals(result1, result2)
        
    def assertResultEqual(self, result1, result2):
        result1 = Result.lift(result1)
        result2 = Result.lift(result2)
        assert_frame_equal(result1.df, result2.df, check_like=True)
        self.assertEquals(result1.aggregations, result2.aggregations)

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

    def get_aggregations(self):
        return {
            key: value for key, value in self.aggregations.items()
        }

    @staticmethod
    def lift(x):
        if isinstance(x, pd.DataFrame):
            return Result(df=x)
        elif isinstance(x, dict):
            return Result(aggregations=x)
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

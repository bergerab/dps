import pandas as pd

from pandas._testing import assert_frame_equal

class ResultAssertions:
    def assertResultEquals(self, result1, result2):
        return self.assertResultEquals(result1, result2)
        
    def assertResultEqual(self, result1, result2):
        result1 = Result.lift(result1)
        result2 = Result.lift(result2)
        if result1.df is not None and result2.df is not None:
            assert_frame_equal(result1.df, result2.df, check_like=True)
        self.assertEquals(result1.aggregations, result2.aggregations)

class Result:
    def __init__(self, df=None, aggregations=None):
        self.df = df
        self.aggregations = {} if aggregations is None else aggregations

    def _merge_aggregations(self, agg):
        aggregations = {}
        for key in self.aggregations:
            aggregations[key] = self.aggregations[key]
        for key in agg:
            aggregations[key] = agg[key]
        return aggregations

    def merge(self, other):
        aggregations = self._merge_aggregations(other.aggregations)
        if other.df is None and self.df is None:
            return Result(aggregations=aggregations)
        if other.df is None and self.df is not None:
            return Result(self.df, aggregations=aggregations)
        if other.df is not None and self.df is None:
            return Result(other.df, aggregations=aggregations)
        return Result(self.df.join(other.df),
                      aggregations)

    def append(self, other):
        aggregations = self._merge_aggregations(other.aggregations)
        if other.df is None and self.df is not None:
            return Result(self.df, aggregations=aggregations)
        if other.df is not None and self.df is None:
            return Result(other.df, aggregations=aggregations)
        return Result(self.df.append(other.df, ignore_index=True),
                      aggregations)

    def equals(self, other):
        return self.df.equals(other.df) and \
               self.aggregations == other.aggregations

    def get_aggregations(self):
        return {
            key: value.get_value() for key, value in self.aggregations.items()
        }

    @staticmethod
    def lift(x):
        if isinstance(x, pd.DataFrame):
            return Result(df=x)
        elif isinstance(x, pd.Series):
            return Result(df=x.to_frame())
        elif isinstance(x, dict):
            return Result(aggregations=x)
        elif isinstance(x, Result):
            return x
        raise Exception(f'Invalid type to lift into a Result type {type(x)}.')

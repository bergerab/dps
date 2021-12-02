import pandas as pd

from .series import Series
from .dataset import Dataset

class Result:
    def __init__(self, dataset=None, aggregations=None, aggregations_for_ui=None):
        self.dataset = dataset
        self.aggregations = {} if aggregations is None else aggregations
        self.aggregations_for_ui = {} if aggregations_for_ui is None else aggregations_for_ui

    def get_merged_aggregations(self, other):
        aggregations = {}
        for key in self.aggregations:
            aggregations[key] = self.aggregations[key]
        for key in other.aggregations:
            aggregations[key] = other.aggregations[key]
            # The below code is commented out because it would cause an extra merge that would throw some aggregations off
            #if key in aggregations:
            #    aggregations[key] = aggregations[key].merge(other.aggregations[key])
            #else:
            #    aggregations[key] = other.aggregations[key]
        return aggregations

    def merge(self, other):
        aggregations = self.get_merged_aggregations(other)
        if other.dataset is None and self.dataset is None:
            return Result(aggregations=aggregations)
        if other.dataset is None and self.dataset is not None:
            return Result(self.dataset, aggregations=aggregations)
        if other.dataset is not None and self.dataset is None:
            return Result(other.dataset, aggregations=aggregations)
        return Result(self.dataset.merge(other.dataset),
                      aggregations)

    def append(self, other):
        aggregations = self._merge_aggregations(other.aggregations)
        if other.dataset is None and self.dataset is not None:
            return Result(self.dataset, aggregations=aggregations)
        if other.dataset is not None and self.dataset is None:
            return Result(other.dataset, aggregations=aggregations)
        return Result(self.dataset.merge(other.dataset),
                      aggregations)

    def equals(self, other):
        return self.dataset.equals(other.dataset) and \
               self.aggregations == other.aggregations

    def get_aggregations_for_ui(self):
        return {
            key: value.get_value() for key, value in self.aggregations_for_ui.items()
        }

    def get_aggregations(self):
        return {
            key: value.get_value() for key, value in self.aggregations.items()
        }

    def get_intermidiate_values(self):
        # Get the series used for the aggregations
        d = {
            key: value.get_series() for key, value in self.aggregations.items() if value.get_series() is not None
        }
        # Get the helper values that were used as well
        df = self.get_dataframe()        
        for column in df:
            d[column] = Series(df[column], times=df.index)
        return Dataset(d)

    def get_dataframe(self):
        if not self.dataset or len(self.dataset.dataset.items()) == 0:
            return pd.DataFrame()
        data = {
            key: value.series for key, value in self.dataset.dataset.items()
        }
        index = list(self.dataset.dataset.values())[0].series.index
        return pd.DataFrame(data=data, index=index)

    @staticmethod
    def lift(x):
        if isinstance(x, Dataset):
            return Result(dataset=x)
        elif isinstance(x, Series):
            return Result(dataset=x.to_dataset(None)) # TODO: pass a name for the dataset?
        elif isinstance(x, dict):
            res = Result()
            res.aggregations_for_ui = x
            return res
        elif isinstance(x, Result):
            return x
        raise Exception(f'Invalid type to lift into a Result type {type(x)}.')

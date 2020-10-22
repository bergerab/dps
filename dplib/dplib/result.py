import pandas as pd

from .series import Series
from .dataset import Dataset

class Result:
    def __init__(self, dataset=None, aggregations=None):
        self.dataset = dataset
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

    def get_aggregations(self):
        return {
            key: value.get_value() for key, value in self.aggregations.items()
        }

    def get_intermidiate_values(self):
        return Dataset({
            key: value.get_series() for key, value in self.aggregations.items()
        })

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
            return Result(aggregations=x)
        elif isinstance(x, Result):
            return x
        raise Exception(f'Invalid type to lift into a Result type {type(x)}.')

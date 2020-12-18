from itertools import chain

import pandas as pd

import dplib.series
import dplib as dp

class Dataset:
    def __init__(self, dataset=None):
        self.dataset = {} if dataset is None else dataset
        
    def set(self, name, series):
        # Disallow null values
        if series is None:
            return self
        self.dataset[name] = series
        return self

    def select(self, names):
        dataset = {}
        for name in names:
            dataset[name] = self.dataset[name]
        return Dataset(dataset)

    def merge(self, other):
        dataset = {}
        for name, value in chain(self.dataset.items(), other.dataset.items()):
            if name in dataset:
                dataset[name] = dataset[name].concat(value)
            else:
                dataset[name] = value
        return Dataset(dataset)

    def rename(self, mappings):
        dataset = {}
        for old_name, new_name in mappings.items():
            dataset[new_name] = self.dataset[old_name]
        return Dataset(dataset)

    def has(self, name):
        return name in self.dataset

    def get(self, name):
        return self.dataset[name]

    def count(self):
        return sum([len(series) for series in self.dataset.values()])

    # Replaces any null columns with empty series
    def fillnull(self):
        d = {}
        for key, value in self.dataset.items():
            if value is None:
                d[key] = dp.Series(pd.Series([]))
            else:
                d[key] = value
        self.dataset = d
        return self

    def to_dataframe(self):
        if len(self.dataset.items()) == 0:
            return pd.DataFrame()

        self.fillnull()

        data = {
            key: value.series for key, value in self.dataset.items()
        }
        values = list(self.dataset.values())
        max_index_len = len(values[0].series.index)
        max_index = values[0].series.index
        for value in values:
            if len(value.series.index) > max_index_len:
                max_index_len = len(value.series.index)
                max_index = value.series.index
        return pd.DataFrame(data=data, index=max_index)

    def __eq__(self, other):
        for name, series in self.dataset.items():
            if name not in other.dataset:
                return False
            if not series.equals(other.dataset[name]):
                return False
        for name, series in other.dataset.items():
            if name not in self.dataset:
                return False
            if not series.equals(self.dataset[name]):
                return False
        return True

    def __repr__(self):
        return repr(self.dataset)

    @staticmethod
    def lift(x):
        if isinstance(x, pd.DataFrame):
            if not isinstance(x.index, pd.DatetimeIndex):
                raise Exception('DataFrame must have an index of type pd.DatetimeIndex')
            data = {}
            for column in x:
                series = x[column]
                data[column] = dplib.series.Series(series, x.index)
            return Dataset(data)
        elif isinstance(x, Dataset):
            return x
        raise Exception(f'Invalid type to lift into a Dataset type {type(x)}.')
            

from itertools import chain

from .series import *

class Dataset:
    def __init__(self, dataset=None):
        self.dataset = {} if dataset is None else dataset
        
    def set(self, name, series):
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
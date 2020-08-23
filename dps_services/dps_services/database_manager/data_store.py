from collections import defaultdict

class DataStore:
    def insert(self, dataset, signals, samples, times):
        raise Exception('Insert unimplemented')

    def execute_queries(self, queries):
        for query in queries:
            self.query(query.dataset, query.signals, \
                       query.interval, query.aggregation)

    def query(self, dataset, signals, interval, aggregation=None):
        raise Exception('Query unimplemented')

class InMemoryDataStore(DataStore):
    '''A DataStore that saves all data into memory (horribly inefficient -- only use for unit testing that the interface works)'''
    def __init__(self):
        self.store = defaultdict(dict)

    def insert(self, dataset, signals, samples, times):
        '''Insert the given samples (at the times'''
        for i, time in enumerate(times):
            sample = samples[i]
            for signal_value in sample:
                self.store.append([signals[i], sample, time])

    def query(self, dataset, signals, interval_from, interval_to, aggregation=None):
        samples = defaultdict(list)
        for signal_name, sample, time in self.store:
            if time >= interval_from and time <= interval_to:
                samples[signal_name].append([signal_name, sample, time])
        return None

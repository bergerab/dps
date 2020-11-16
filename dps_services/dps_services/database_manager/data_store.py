import dps_services.util as util

from .query import load_query_json
from .delete import load_delete_json

class DataStore:
    def __init__(self, validate_inserts=False):
        self.validate_inserts = validate_inserts

    @staticmethod
    def to_results_response(results):
        return {
            'results': list(map(lambda x: x.to_dict(), results))
        }
    
    @classmethod
    def insert(DataStoreClass, insert_request):
        ds = DataStoreClass()
        ds.execute_inserts(insert_request)
    
    @classmethod
    def query(DataStoreClass, query_request):
        ds = DataStoreClass()
        results = ds.execute_queries(load_query_json(query_request))
        return DataStore.to_results_response(results)

    @classmethod
    def delete(DataStoreClass, delete_request):
        ds = DataStoreClass()
        ds.execute_delete(load_delete_json(delete_request))

    @classmethod
    def execute_get_signal_names(DataStoreClass, request):
        ds = DataStoreClass()
        results = GetSignalNamesResult()
        ds.get_signal_names(results, request['dataset'], request['query'], request['limit'], request['offset'])
        return DataStore.to_results_response([results])

    def execute_delete(self, delete):
        self.delete_dataset(delete.dataset)

    def execute_inserts(self, inserts):
        for insert in inserts:
            self.insert_signals(insert.dataset, insert.signals, \
                                insert.samples, insert.times, insert.upsert)

    def execute_queries(self, queries):
        '''
        :returns: a list of `Result` objects
        '''
        results = []
        for query in queries:
            if query.aggregation is None:
                result = SignalQueryResult(query)
                self.fetch_signals(result, \
                                   query.dataset, query.signals, \
                                   query.interval, query.limit)
            else:
                result = AggregateQueryResult(query)
                self.aggregate_signals(result, \
                                   query.dataset, query.signals, \
                                   query.interval, \
                                   aggregation=query.aggregation)
            results.append(result)
        return results
    
    def insert_signals(self, dataset, signals, samples, times):
        raise Exception('DataStore.insert_signals not implemented.')

    def fetch_signals(self, result, dataset_name, signal_names, interval, limit):
        '''
        Writes the results of the query to the `SignalQueryResult` object (using `results.add(values, time)`)
        '''
        raise Exception('DataStore.fetch_signals not implemented.')

    def get_signal_names(self, result, dataset_name):
        '''
        Writes the results of the query to the `GetSignalNamesResult` object (using `results.add(name)`)
        '''
        raise Exception('DataStore.get_signal_names not implemented.')

    def aggregate_signals(self, result, dataset_name, signal_names, interval, aggregation):
        '''
        Writes the results of the query to the `AggregateQueryResult` object (using `results.set(signal_name, value)`)
        '''
        raise Exception('DataStore.aggregate_signals not implemented.')

    def delete_dataset(self, dataset_name):
        '''
        Deletes a dataset, and all data that is associated with that dataset.

        NOTE: Only implement this method if you wish to support the integration tests.
              This method can be left unimplemented in production systems. It is only for testing purposes.
        '''
        raise Exception('DataStore.delete_dataset not implemented.')

class SignalQueryResult:
    def __init__(self, query):
        self.query = query
        self.times = []
        self.samples = []
        self.signals = query.signals
        self.previous_time = None
        
    def add(self, values, time, validate=True):
        if validate:
            if len(values) != len(self.signals):
                raise Exception('Must provide a value for every signal value.')
            else:
                self.previous_time = time
        self.times.append(time)
        self.samples.append(values)

    def to_dict(self):
        return {
            'samples': self.samples,
            'times': list(map(lambda x: util.format_datetime(x), self.times)),
            'query': self.query.to_dict()
        }

class AggregateQueryResult:
    def __init__(self, query):
        self.query = query
        self.results = { signal: 0 for signal in self.query.signals }

    def set(self, signal_name, value):
        if signal_name not in self.results:
            raise Exception(f'Invalid signal name {util.quoted(signal_name)}.')
        self.results[signal_name] = value

    def to_dict(self):
        return {
            'values': list(self.results.values()),
            'query': self.query.to_dict()
        }

class GetSignalNamesResult:
    def __init__(self):
        self.results = []
        self.total = 0

    def add(self, name):
        self.results.append(name)

    def set_total(self, total):
        self.total = total

    def to_dict(self):
        return {
            'values': self.results,
            'total': self.total,
        }

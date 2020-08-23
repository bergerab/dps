import dps_services.util as util

class DataStore:
    def execute_inserts(self, inserts):
        for insert in inserts:
            self.insert(insert.dataset, insert.signals, \
                       query.interval, query.aggregation)
    
    def insert(self, dataset, signals, samples, times):
        raise Exception('DataStore.insert unimplemented')

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
                                   query.interval)
            else:
                result = AggregateQueryResult(query)
                self.aggregate_signals(result, \
                                   query.dataset, query.signals, \
                                   query.interval, \
                                   aggregation=query.aggregation)
            results.append(result)
        return results

    def fetch_signals(self, result, dataset, signals, interval):
        '''
        Writes the results of the query to the `SignalQueryResult` object (using `results.add(values, time)`)
        '''
        raise Exception('DataStore.fetch_signals unimplemented')

    def aggregate_signals(self, result, dataset, signals, interval, aggregation):
        '''
        Writes the results of the query to the `AggregateQueryResult` object (using `results.add(value)`)
        '''
        raise Exception('DataStore.aggregate_signals unimplemented')

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
                raise Exception('Must provide a value for all signal values in each call.')
            if time < self.query.interval.start or time > self.query.interval.end:
                start = util.quoted(self.query.interval.start)
                end = util.quoted(self.query.interval.end)
                raise Exception(f'Given time {util.quoted(time)} is out-of-bounds of the query interval (between {start} and {end}).')
            if self.previous_time and time <= self.previous_time:
                raise Exception(f'Received time value {util.quoted(time)} in non-monotonically increasing order.')
            else:
                self.previous_time = time
        self.times.append(time)
        self.samples.append(values)

    def to_dict(self):
        return {
            'samples': self.samples,
            'times': self.times,
            'query': self.query.to_dict()
        }

class AggregateQueryResult:
    def __init__(self, query):
        self.query = query
        self.results = []

    def add(self, value):
        self.results.append(value)

    def to_dict(self):
        return {
            'results': self.results,
            'query': self.query.to_dict()
        }

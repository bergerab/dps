import json

import dps_services.util as util

class Query:
    def __init__(self, dataset, signals, interval, aggregation=None):
        self.dataset = dataset
        self.signals = signals
        self.interval = interval
        self.aggregation = aggregation

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.dataset == other.dataset and \
                   self.signals == other.signals and \
                   self.interval == other.interval and \
                   self.aggregation == other.aggregation
        return False

    def __repr__(self):
        return f'Query(dataset={self.dataset}, signals={self.signals}, interval={self.interval}, aggregation={self.aggregation})'

    def to_dict(self):
        d = {
            'dataset': self.dataset,
            'signals': self.signals,
            'interval': self.interval.to_dict()
        }
        if self.aggregation:
            d['aggregation'] = self.aggregation
        return d
            
class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.start == other.start and self.end == other.end
        return False

    def __repr__(self):
        return f'Interval(start={self.start}, end={self.end})'

    def to_dict(self):
        return {
            'start': util.format_datetime(self.start),
            'end': util.format_datetime(self.end),
        }
    
def parse_query_json(json_string):
    '''
    Parses a JSON string of queries, and returns a list of query objects
    
    :params json_string: the JSON string containing the request
    '''
    jo = json.loads(json_string)
    return load_query_json(jo)

def load_query_json(query_json):
    '''
    Given a Python dictionary representing a query, produces a Query object
    
    :params query: the dictionary containing the request
    :returns: a list of Query objects
    '''
    with util.RequestValidator(query_json) as validator:
        queries = []        
        sub_query_jsons = validator.require('queries', list, default=[])
        for i, sub_query_json in enumerate(sub_query_jsons):
            with validator.scope_list('queries', i):
                dataset = validator.require('dataset', str)
                signals = validator.require('signals', list)
                interval = validator.require('interval', object)
                with validator.scope('interval'):
                    interval_start = validator.require('start', datetime_format_string=util.DATETIME_FORMAT_STRING)
                    interval_end = validator.require('end', datetime_format_string=util.DATETIME_FORMAT_STRING)
                aggregation = validator.require('aggregation', str, optional=True,
                                                one_of=['average', 'count', 'min', 'max'])
            queries.append(Query(dataset, signals, Interval(interval_start, interval_end), aggregation))
        return queries

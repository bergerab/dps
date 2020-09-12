import json

import dps_services.util as util

class Insert:
    def __init__(self, dataset, signals, samples, times):
        self.dataset = dataset
        self.signals = signals
        self.samples = samples
        self.times = times

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.dataset == other.dataset and \
                   self.signals == other.signals and \
                   self.samples == other.samples and \
                   self.times == other.times
        return False

    def __repr__(self):
        return f'Insert(dataset={self.dataset}, signals={self.signals}, samples={self.samples}, times={self.times})'

    def to_dict(self):
        return {
            'dataset': self.dataset,
            'signals': self.signals,
            'samples': self.samples,            
            'times': self.times,
        }
            
def parse_insert_json(json_string):
    '''
    Parses a JSON string of inserts, and returns a list of insert objects
    
    :params json_string: the JSON string containing the request
    '''
    jo = json.loads(json_string)
    return load_insert_json(jo)

def load_insert_json(insert_json):
    '''
    Given a Python dictionary representing an insert, produces a Insert object
    
    :params query: the dictionary containing the request
    :returns: a list of Insert objects
    '''
    with util.RequestValidator(insert_json) as validator:
        inserts = []        
        sub_insert_jsons = validator.require('inserts', list, default=[])
        for i, sub_insert_json in enumerate(sub_insert_jsons):
            with validator.scope_list('inserts', i):
                dataset = validator.require('dataset', str)
                signals = validator.require('signals', list)
                samples = validator.require('samples', list)
                times = validator.require('times', list, datetime_format_string=util.DATETIME_FORMAT_STRING)
            inserts.append(Insert(dataset, signals, samples, times))
        return inserts

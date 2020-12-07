import json

import dps_services.util as util

class Delete:
    def __init__(self, dataset):
        self.dataset = dataset

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.dataset == other.dataset
        return False

    def __repr__(self):
        return f'Delete(dataset={self.dataset})'

    def to_dict(self):
        return {
            'dataset': self.dataset,
        }
            
def parse_delete_json(json_string):
    '''
    Parses a JSON string of a delete request, and returns a delete object
    
    :params json_string: the JSON string containing the request
    '''
    jo = json.loads(json_string)
    return load_delete_json(jo)

def load_delete_json(delete_json):
    '''
    Given a Python dictionary representing an dataset delete, produces a Delete object
    
    :params query: the dictionary containing the request
    :returns: a Delete object
    '''
    with util.RequestValidator(delete_json) as validator:
        dataset = validator.require('dataset', str, default='', optional=True)
        return Delete(dataset)

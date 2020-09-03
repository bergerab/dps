'''DPS Client - A client for communicating with the DPS Manager, and sending signal data.'''
import requests

from datetime import datetime

class Client:
    '''A connection to the DPS Manager.'''
    def __init__(self, url, dataset):
        self.url = _normalize_url(url)
        self.dataset = dataset
        self.batches = []

    def make_batch(self, time=datetime.utcnow()):
        '''Create a :class:`BatchClient` for sending multiple signal values
        at the same time (more efficient and organizes the time values for ease of processing).
        '''
        batch = BatchClient(self, time)
        self.batches.append(batch)
        return batch

    def _flush(self):
        '''
        Collects all batch requests into a request dictionary.
        '''
        signal_names = set()
        for batch in self.batches:
            signal_name_to_value = batch.signal_name_to_value
            for signal_name in signal_name_to_value:
                signal_names.add(signal_name)
        signal_names = list(signal_names)

        batches = []
        for batch in self.batches:
            signal_name_to_value = batch.signal_name_to_value
            batch = []
            for signal_name in signal_names:
                if signal_name in signal_name_to_value:
                    batch.append(signal_name_to_value[signal_name])
                else:
                    batch.append(0.0)
            batches.append(batch)

        times = []
        for batch in self.batches:
            times.append(str(batch.time))

        # Reset batch clients
        self.batches = []
        
        return {
            'dataset': self.dataset,
            'signals': signal_names,
            'samples': batches,
            'times': times,
        }

    def send(self):
        return requests.post(self.url + 'insert', json={
            'inserts': [
                self._flush()
            ]
        })

class BatchClient:
    def __init__(self, client, time):
        self.client = client
        self.time = time
        self.signal_name_to_value = {}
    
    def add(self, signal_name, value):
        self.signal_name_to_value[signal_name] = value

def _normalize_url(url):
    if url[-1] != '/':
        url += '/'
    return url
    
def connect(url, dataset):
    '''Connects to a DPS Manager.

    :param url: The URL of the DPS Manager
    :returns: A :class:`Client`
    '''
    return Client(url, dataset)

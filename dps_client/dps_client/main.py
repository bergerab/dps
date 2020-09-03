'''DPS Client - A client for communicating with the DPS Manager, and sending signal data.'''
import requests

from datetime import datetime

class Client:
    '''A connection to the DPS Manager.'''
    def __init__(self, url, dataset):
        self.url = url
        if url[-1] != '/':
            url += '/'
        
        self.dataset = dataset
        self.batch_clients = []

    def create_batch_client(self, time=datetime.utcnow()):
        '''Create a :class:`BatchClient` for sending multiple signal values
        at the same time (more efficient and organizes the time values for ease of processing).
        '''
        batch_client = BatchClient(self, time)
        self.batch_clients.append(batch_client)
        return batch_client

    def send(self):
        signal_names = set()
        for batch_client in self.batch_clients:
            signal_name_to_value = batch_client.signal_name_to_value
            for signal_name in signal_name_to_value:
                signal_names.add(signal_name)
        signal_names = list(signal_names)

        batches = []
        for batch_client in self.batch_clients:
            signal_name_to_value = batch_client.signal_name_to_value
            batch = []
            for signal_name in signal_names:
                if signal_name in signal_name_to_value:
                    batch.append(signal_name_to_value[signal_name])
                else:
                    batch.append(0.0)
            batches.append(batch)

        times = []
        for batch_client in self.batch_clients:
            times.append(str(batch_client.time))

        # Reset batch clients
        self.batch_clients = []
        
        return requests.post(self.url + 'insert', json={
            'inserts': [
                {
                    'dataset': self.dataset,
                    'signals': signal_names,
                    'samples': batches,
                    'times': times,
                }
            ]
        })

class BatchClient:
    def __init__(self, client, time):
        self.client = client
        self.time = time
        self.signal_name_to_value = {}
    
    def add(self, signal_name, value):
        self.signal_name_to_value[signal_name] = value
    
def connect(url, dataset):
    '''Connects to a DPS Manager.

    :param url: The URL of the DPS Manager
    :returns: A :class:`Client`
    '''
    return Client(url, dataset)

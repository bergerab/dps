'''DPS Client - A client for communicating with the DPS Manager, and sending signal data.'''
import requests
import pandas as pd

from datetime import datetime, timedelta

from google.protobuf.json_format import MessageToJson
from google.protobuf.timestamp_pb2 import Timestamp

from .insert_pb2 import InsertRequest, Samples, Batch



DATETIME_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%f'
'''
The datetime format used in JSON requests.

Example: 2020-06-30 03:54:45.175489 means June 30th, 2020 at 3:54:45AM and 175489 microseconds.
'''

class Client:
    '''
    A connection to the DPS Database Manager.

    Protocol can be either "protobuf" or "json"
    '''
    def __init__(self, url, dataset='', protocol='protobuf'):
        self.url = _normalize_url(url)
        self.dataset = dataset
        self.batches = []
        self.protocol = protocol

    def make_batch(self, time=None):
        '''Create a :class:`BatchClient` for sending multiple signal values
        at the same time (more efficient and organizes the time values for ease of processing).
        '''
        if time is None:
            time = datetime.utcnow()        
        batch = BatchClient(self, time)
        self.batches.append(batch)
        return batch

    def send_csv(self, filepath, time_column, batch_size=400000, start_time=None, timestep_units='s', verbose=False, columns=None):
        '''
        Sends the CSV to the client's URL in batches.

        If `start_time` is specified, it is assumed that the `time_column` represents a relative time
        (e.g. time since the data collection began). The `start_time` will be used to create absolute timestamps
        where the `time_column` is delta time.

        Otherwise, it is assumed `time_column` is an absolute date.

        `columns` allows for only sending certain columns to the database (set it to a list of strings where the strings match
        column names).
        '''
        if start_time is None and timestep_units is not None:
            raise Exception('`start_time` is required when specifying `timestep_units`.')
        
        if start_time is None:
            df = pd.read_csv(filepath, parse_dates=[time_column])
        else:
            df = pd.read_csv(filepath)
            
        row_count = len(df)
        sent_count = 0.0

        column_names = [key for key in df if key != time_column or (columns is not None and key not in columns)]

        for _, row in df.iterrows():
            if start_time is None:
                batch = self.make_batch(row[time_column])
            else:
                offset = timestep_units_to_timedelta(row[time_column], timestep_units)
                batch = self.make_batch(start_time + offset)

            for name in column_names:
                batch.add(name, row[name])
            if len(self.batches) * len(column_names) >= batch_size:
                sent_count += len(self.batches)
                self.send()
                if verbose:
                    print(f'send_csv: {(sent_count / row_count) * 100}% complete.')
        self.send()

    def _flush(self, datetimes_to_string=True):
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
            if datetimes_to_string:                
                times.append(datetime.strftime(batch.time, DATETIME_FORMAT_STRING))
            else:
                times.append(batch.time)

        # Reset batch clients
        self.batches = []
        
        return {
            'dataset': self.dataset,
            'signals': signal_names,
            'samples': batches,
            'times': times,
        }

    def send(self):
        url = self.url + 'insert'
        
        if self.protocol == 'protobuf':
            o = self._flush(False)
            inserts_request = InsertRequest()
            insert_request = inserts_request.inserts.add()
            insert_request.dataset = self.dataset

            insert_request.signals.extend(o['signals'])

            for time in o['times']:
                ts = Timestamp()
                ts.FromDatetime(time)
                insert_request.times.append(ts)

            samples_request = insert_request.samples
            for batch in o['samples']:
                batch_request = samples_request.batches.add()
                batch_request.value.extend(batch)

            pb_string = inserts_request.SerializeToString()
            return requests.post(url, data=pb_string, headers={
                'Content-Type': 'application/protobuf',
            })
        elif self.protocol == 'json':
            o = self._flush()
            response = requests.post(url, json={
                'inserts': [
                    o
                ]
            })
            if response.status_code != 200:
                raise Exception(response.text)
        else:
            raise Exception(f'Invalid DPS Client protocol "{self.protocol}"')

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
    url += 'api/v1/'
    return url
    
def connect(url, dataset):
    '''Connects to a DPS Manager.

    :param url: The URL of the DPS Manager
    :returns: A :class:`Client`
    '''
    return Client(url, dataset)

def timestep_units_to_timedelta(n, units):
    if units == 's':
        return timedelta(seconds=n)
    elif units == 'ms':
        return timedelta(milliseconds=n)
    else:
        raise Exception(f'Unsupported timestep unit of "{units}".')

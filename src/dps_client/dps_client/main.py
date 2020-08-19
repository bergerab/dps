'''
DPS Client - A client for communicating with the DPS Manager, and sending signal data.

The client is broken up into several sub-clients each for performing different tasks.

First there is `Client` which is for sending and receiving metadata directly to the DPS Manager.

Then there is `DeviceClient` (that can be created by calling `create_device_client` on a `Client`) which is for sending signal data.

Finally there is `BulkClient` (that can be created by calling `create_bulk_client` on a `DeviceClient`) for sending many signal samples all collected at the same time. This improves performance, as multiple signal values can be sent in a signal web request.
'''

from datetime import datetime

class Client:
    '''
    A connection to the DPS Manager.
    '''
    def __init__(self, url):
        self.url = url

    def create_device_client(self, device_uid, validate=False):
        '''
        Create a device client given a device's unique identifier (UID)
        '''
        if validate:
            # ask DPS if the device_uid is a valid one
            raise Exception('Unimplemented')
        return DeviceClient(self, device_uid)
    
class DeviceClient:
    '''
    A client for sending signal data to DPS using a device's unique identifier (UID)
    '''
    def __init__(self, dps_client, device_uid):
        self.dps_client = dps_client
        self.device_uid = device_uid

    def create_bulk_client(self, time=datetime.utcnow()):
        '''
        Create a BulkClient for sending multiple signal values at the same time (more efficient and organizes the time values for ease of processing).
        '''
        return BulkClient(time)

    def send_sample(self, signal_uid, value, time):
        pass

class BulkClient:
    '''
    A client that accumulates many samples under a single time and sends them together to DPS.

    This is more efficient than sending samples individually, and is necessary for matching many samples with the same time (for point-wise computations).
    '''
    def __init__(self, device_client, time):
        self.device_client = device_client
        self.time = time
        self.samples = []
    
    def add(self, signal_uid, value):
        '''
        Queue the value to be sent with the bulk request (where all values share the same time).
        '''
        self.samples.append(Sample(signal_uid, value, self.time))

    def send_samples(self):
        pass

class Sample:
    def __init__(self, signal_uid, value, time):
        self.signal_uid = signal_uid
        self.value = value
        self.time = time
    
def connect(url):
    '''
    Connects to a DPS server. Returns a client.
    '''
    return Client(url)

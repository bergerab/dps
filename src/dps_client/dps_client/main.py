'''
DPS Client - A client for communicating with the DPS Manager, and sending signal data.

The client is broken up into several sub-clients each for performing different tasks.

First there is `DPSClient` which is for sending and receiving metadata directly to the DPS Manager.

Then there is `DPSDeviceClient` (that can be created by calling `create_device_client` on a `DPSClient`) which is for sending signal data.

Finally there is `DPSBulkClient` (that can be created by calling `create_bulk_client` on a `DPSDeviceClient`) for sending many signal samples all collected at the same time. This improves performance, as multiple signal values can be sent in a signal web request.
'''

from datetime import datetime

class DPSClient:
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
        return DPSDeviceClient(self, device_uid)
    
class DPSDeviceClient:
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

    def send(self, value, time):
        pass

class DPSBulkClient:
    '''
    A client that accumulates many samples under a single time and sends them together to DPS.

    This is more efficient than sending samples individually, and is necessary for matching many samples with the same time (for point-wise computations).
    '''
    def __init__(self, device_client, time):
        self.device_client = device_client
        self.time = time
        self.values = []
    
    def add(self, value):
        '''
        Queue the value to be sent with the bulk request (where all values share the same time).
        '''
        self.values.append(value)

    def send(self):
        pass
        
    
def connect(url):
    '''
    Connects to a DPS server. Returns a client.
    '''
    return DPSClient(url)

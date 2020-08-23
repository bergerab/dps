'''DPS Client - A client for communicating with the DPS Manager, and sending signal data.

The client is broken up into several sub-clients each for performing different tasks.

First there is `Client` which is for sending and receiving metadata directly to the DPS Manager.

Then there is `DeviceClient` (that can be created by calling `create_device_client` on a
`Client`) which is for sending signal data.

Finally there is `BulkClient` (that can be created by calling `create_bulk_client` on a
`DeviceClient`) for sending many signal samples all collected at the same time. This improves
 performance, as multiple signal values can be sent in a signal web request.
'''

from datetime import datetime

class Client:
    '''A connection to the DPS Manager.'''
    def __init__(self, url):
        self.url = url

    def create_device_client(self, device_uid, validate=False):
        '''Creates a new :class:`DeviceClient` to send signal data for a device.

        :param device_uid: the unique identifier of the device
        :param validate: whether or not to validate that the unique device identifier is registered on the DPS Manager

        :returns: A :class:`DeviceClient`
        '''
        if validate:
            # ask DPS if the device_uid is a valid one
            raise Exception('Unimplemented')
        return DeviceClient(self, device_uid)

client = Client('https://dps-manager-url/')
device_client = client.create_device_client('inverter-a')

device_client.send_sample('va', 2.4324817)

bc = device_client.create_bulk_client()
bc.add('va', 2.4358237)
bc.add('vb', 4.5327239)
bc.add('vc', 8.5938727)
bc.send()

class DeviceClient:
    '''A client for sending signal data to DPS using a device's unique identifier (UID)
    '''
    def __init__(self, dps_client, device_uid):
        self.dps_client = dps_client
        self.device_uid = device_uid

    def create_bulk_client(self, time=datetime.utcnow()):
        '''Create a :class:`BulkClient` for sending multiple signal values
        at the same time (more efficient and organizes the time values for ease of processing).
        '''
        return BulkClient(time)

    def send_sample(self, signal_uid, value, time):
        '''Sends a single sample (a value tagged with a time) for the a signal.

        :param signal_uid: The unique identifier for the signal.
        :param value: The value of the signal at one moment.
        :param time: The moment that the value was sampled.
        '''
        pass

class BulkClient:
    '''A client that accumulates many samples under a single time
    and sends them together to DPS.

    This is more efficient than sending samples individually, and
    is necessary for matching many samples with the same time
    (for point-wise computations).
    '''
    def __init__(self, device_client, time):
        self.device_client = device_client
        self.time = time
        self.samples = []
    
    def add(self, signal_uid, value):
        '''Queue the value to be sent with the bulk request
        (where all values share the same time).

        
        '''
        self.samples.append(Sample(signal_uid, value, self.time))

    def send(self):
        '''Sends the bulk request (a collection of samples with the same time).'''
        pass

class Sample:
    '''
    '''
    def __init__(self, signal_uid, value, time):
        self.signal_uid = signal_uid
        self.value = value
        self.time = time
    
def connect(url):
    '''Connects to a DPS Manager.

    :param url: The URL of the DPS Manager
    :returns: A :class:`Client`
    '''
    return Client(url)

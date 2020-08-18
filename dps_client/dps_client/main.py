'''
How to tell the server which signal/system this client is reporting?

Use a string identifier?

client.send_sample()
'''

class DPSClient:
    def __init__(self, url):
        pass

    def send_sample(self, value, time):
        pass

def connect(url):
    '''
    Connects to a DPS server. Returns a client.
    '''
    return DPSClient(url)

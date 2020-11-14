from datetime import datetime, timedelta

from dps_client import Client
from timeit import timeit

def doit():
    dpc = Client('http://localhost:3002', '', protocol='protobuf')
    
    start_time = datetime.now() - timedelta(hours=1)
    for x in range(300000):
        batch = dpc.make_batch(start_time + timedelta(seconds=x))
        batch.add('PINK1', x/2)
        batch.add('PINK2', x*2)
        batch.add('PINK3', x+2)
    dpc.send()

timeit(doit, number=1)

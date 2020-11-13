from datetime import datetime, timedelta

from dps_client import Client
from timeit import timeit

def doit():
    dpc = Client('http://localhost:3002', '', protocol='protobuf')
    
    start_time = datetime.now() - timedelta(hours=1)
    for x in range(200000):
        batch = dpc.make_batch(start_time + timedelta(seconds=x))
        batch.add('DINKA', x/2)
        batch.add('DINKB', x*2)
        batch.add('DINKC', x+2)
    dpc.send()

timeit(doit, number=1)

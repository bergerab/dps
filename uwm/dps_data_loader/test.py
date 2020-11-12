from datetime import datetime, timedelta

from dps_client import Client
from timeit import timeit

def doit():
    dpc = Client('http://localhost:3002', '')
    
    start_time = datetime.now() - timedelta(hours=1)
    for x in range(1000):
        batch = dpc.make_batch(start_time + timedelta(seconds=x))
        batch.add('A', x/2)
        batch.add('B', x*2)
        batch.add('C', x+2)
    dpc.send()

timeit(doit, number=1)

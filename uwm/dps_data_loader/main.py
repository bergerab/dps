from datetime import datetime, timedelta

from dps_client import Client

dpc = Client('http://localhost:3001', '', protocol='json')

start_time = datetime.now() - timedelta(hours=1)
for x in range(100000):
    batch = dpc.make_batch(start_time + timedelta(seconds=x))
    batch.add('A', x/2)
    batch.add('B', x*2)
    batch.add('C', x+2)
dpc.send()

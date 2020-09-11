import dps_client

from datetime import datetime, timedelta

URL = 'http://bergerab.com/dps/db/api/v1/'

client = dps_client.connect(URL, 'LabVIEW Device')

for i in range(100):
    batch = client.create_batch_client(datetime.now() + timedelta(microseconds=i))
    batch.add('Signal A', 1.2)
    batch.add('Signal B', 1.3)

client.send()

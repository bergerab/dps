import dps_client
from datetime import datetime

URL = 'http://bergerab.com/dps/db/api/v1/'
client = dps_client.connect(URL, 'Adam Test')

batch = client.make_batch(datetime.now())
batch.add('Signal A', 1.2)
batch.add('Signal B', 1.3)

print(client.send())

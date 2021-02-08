import os

from flask import Flask, request, jsonify

import dps_client

app = Flask(__name__)

DBM_URL = os.getenv('DBM_URL')
if not DBM_URL:
    raise Exception('A DPS Database Manager URL is required (set via DBM_URL environment variable).')
DPSMANURL = os.getenv('DPS_MANAGER_URL')
if not DPSMANURL:
    raise Exception('A DPS Manager URL is required (set via DPS_MANAGER_URL environment variable).')
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise Exception('An API key is required (set via API_KEY environment variable).')
DEBUG = bool(os.getenv('DPS_RELAY_DEBUG', False))
SEND_THRESHOLD = int(os.getenv('SEND_THRESHOLD', 10000))

print('Using DPS database manager URL: ' + DBM_URL)
print('Using DPS manager manager URL: ' + DPSMANURL)
print('Using threshold of: ' + str(SEND_THRESHOLD))

clients = {}

@app.route('/', methods=['GET'])
def info():
    return jsonify({
        'dbm_url': DBM_URL,
        'dps_manager_url': DPSMANURL,
        'send_threshold': SEND_THRESHOLD,
        'type': 'dps_relay',
        'debug': DEBUG,
    })

# TODO: add timer that runs every minute or so
# that will call client.send()
# add a mutex around client.send() for both
# the ingest endpoint and this timer

# The timer should also pull down the schedules
# on a regular interval

@app.route('/ingest', methods=['GET', 'POST'])
def ingest():
    if request.method == 'GET':
        data = request.args.get('data')
    else:
        data = request.data.decode()

    data = data.split(';')
    device_name = data[0]
    signal_sample_pairs = data[1:]
        
    if device_name in clients: client = clients[device_name]
    else: client = clients[device_name] = dps_client.connect(DBM_URL, device_name, API_KEY)
        
    batch = client.make_batch()
    for x in range(0, len(signal_sample_pairs)//2):
        x = x*2
        batch.add(signal_sample_pairs[x], float(signal_sample_pairs[x+1]))

    # only send after a certain amount of data is buffered
    if len(client.batches) >= SEND_THRESHOLD:
        response = client.send()
        if response.status_code != 500:
            print(response.text)

    return 'OK'

if __name__ == '__main__':
   app.run(debug=DEBUG)

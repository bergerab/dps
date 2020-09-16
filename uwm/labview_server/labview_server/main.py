import os

from flask import Flask, request, jsonify

import dps_client

app = Flask(__name__)

URL = os.getenv('DBM_URL', 'http://bergerab.com/dps/db/')
DEBUG = bool(os.getenv('LABVIEW_INTEGRATION_DEBUG', False))
SEND_THRESHOLD = os.getenv('LABVIEW_INTEGRATION_SEND_THRESHOLD', 2)

print('Using database manager URL: ' + URL)
print('Using threshold of: ' + str(SEND_THRESHOLD))

clients = {}

@app.route('/', methods=['GET'])
def info():
    return jsonify({
        'dbm_url': URL,
        'send_threshold': SEND_THRESHOLD,
        'type': 'labview-integration',
        'debug': DEBUG,
    })

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
    else: client = clients[device_name] = dps_client.connect(URL, device_name)
        
    batch = client.make_batch()
    for x in range(0, len(signal_sample_pairs)//2):
        x = x*2
        batch.add(signal_sample_pairs[x], float(signal_sample_pairs[x+1]))

    print('Added ' + str(data))

    # only send after a certain amount of data is buffered
    if len(client.batches) >= SEND_THRESHOLD:
        print('SENDING')
        response = client.send()
        print(response)
        if response.status_code is not 500:
            print(response.text)

    return 'OK'

if __name__ == '__main__':
   app.run(debug=DEBUG)

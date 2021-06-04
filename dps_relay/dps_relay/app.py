import os
import csv
import io

import asyncio
from aiohttp import web

from signal import SIGINT, SIGTERM

import dps_client
from dateutil.parser import parse

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
SEND_THRESHOLD = int(os.getenv('DPS_RELAY_SEND_THRESHOLD', 100000))

print('Using DPS database manager URL: ' + DBM_URL)
print('Using DPS manager manager URL: ' + DPSMANURL)
print('Using threshold of: ' + str(SEND_THRESHOLD))

clients = {}

cache = {}

# The body of the request should be a CSV file where the header has signal names
# and each column has the signal value
#
# There MUST be a time column called "Time" with a time format readable by python's "dateutil" module
async def http(request):
    dataset_name = request.rel_url.query['dataset']
    
    # if dataset_name in clients:
    #     client = clients[dataset_name]
    # else:
    #     client = clients[dataset_name] = dps_client.connect(DBM_URL, dataset_name, API_KEY)

    dataset_cache = []
    if dataset_name in cache:
        dataset_cache = cache[dataset_name]
    else:
        dataset_cache = cache[dataset_name] = []

    data = await request.text()

    reader = csv.DictReader(io.StringIO(data))
    dataset_cache.extend(reader)
        # time = parse(row['Time'])
        # dataset_cache
        # batch = client.make_batch(time)        
        # del row['Time'] # remove the Time value so we don't send it twice
        # for signal_name in row.keys():
        #     batch.add(signal_name, row[signal_name])
    print(len(dataset_cache))
        
    return web.Response(text="OK")

async def ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
    return ws

async def info():
    return jsonify({
        'dbm_url':         DBM_URL,
        'dps_manager_url': DPSMANURL,
        'send_threshold':  SEND_THRESHOLD,
        'type':           'dps_relay',
        'debug':           DEBUG,
    })

# TODO: do this in a separate task
# on some interval, send all cached values
# if len(client.batches) >= SEND_THRESHOLD:
#     response = client.send()
#     if response.status_code != 500:
#         print(response.text)

app = web.Application(client_max_size=4096**2)
app.add_routes([web.get('/ws', ws)])
app.add_routes([web.post('/http', http)])
app.add_routes([web.get('/info', info)])

# Hack for Windows, so that SIGINT is respected
def wakeup():
    loop.call_later(0.1, wakeup)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(0.1, wakeup)
    asyncio.set_event_loop(loop)
    web.run_app(app, handle_signals=True)

# # TODO: add timer that runs every minute or so
# # that will call client.send()
# # add a mutex around client.send() for both
# # the ingest endpoint and this timer

# # The timer should also pull down the schedules
# # on a regular interval

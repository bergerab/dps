import json

import dps_services.util as ddt

from .util import *

class APIClient:
    def __init__(self, url, key):
        # Ensure URL ends with a slash
        if url[-1] != '/':
            url += '/'
        self.url = url
        self.key = key

    async def get(self, session, postfix):
        resp = await session.get(self.url + postfix)
        return json.loads(await resp.text())

    async def post(self, session, postfix, data):
        resp = await session.post(self.url + postfix, json=data, headers={
            'Authentication': 'API ' + self.key,
        })
        if resp.status == 404:
            return 404
        return json.loads(await resp.text())

    async def put(self, session, postfix, id, data):
        resp = await session.put(self.url + postfix + '/' + str(id), json=data)
        if resp.status == 404:
            return 404
        return json.loads(await resp.text())

STATUS_ERROR    = 0
STATUS_RUNNING  = 1
STATUS_COMPLETE = 2
STATUS_QUEUED   = 3
class DPSManagerAPIClient(APIClient):
    POP_JOB_POSTFIX  = 'api/v1/pop_job'
    RESULT_POSTFIX   = 'api/v1/result'
    
    async def send_result(self, session, batch_process_id, aggregations, inter_results, status=0, message=None, result_id=None, processed_samples=None, total_samples=None):
        if status not in [STATUS_ERROR, STATUS_RUNNING, STATUS_COMPLETE]:
            raise Exception('Invalid result status. Must be either STATUS_ERROR=0, STATUS_RUNNING=1, or STATUS_COMPLETE=2.')
        results = dict_to_mappings(aggregations, inter_results)
        data = {
            'batch_process_id': batch_process_id,
            'results':          results,
            'status':           status,
        }
        if processed_samples is not None:
            data['processed_samples'] = processed_samples
        if total_samples is not None:
            data['total_samples'] = total_samples
        if message is not None:
            data['message'] = message
        if result_id is None:
            return await self.post(session, self.RESULT_POSTFIX, data)
        else:
            return await self.put(session, self.RESULT_POSTFIX, result_id, data)

    async def pop_job(self, session):
        return await self.get(session, self.POP_JOB_POSTFIX)

class DatabaseManagerAPIClient(APIClient):
    '''
    An API client for a DPS Database Manager server.

    Ideally this wouldn't be necessary, and I would simply use DPS Client to send data.
    However, this program is written using asyncio, and requires asynchronous HTTP requests.
    '''
    INSERT_POSTFIX  = 'api/v1/insert'
    QUERY_POSTFIX   = 'api/v1/query'

    async def get_data(self, session, dataset, signals, start_time, end_time, limit=None):
        data = {
            "queries": [
                {
                    "dataset": dataset,
                    "signals": signals,
                    "interval": {
                        "start": ddt.format_datetime(start_time),
                        "end": ddt.format_datetime(end_time),
                    },
                }
            ]
        }

        if limit:
            data['queries'][0]['limit'] = limit
        result = await self.post(session, self.QUERY_POSTFIX, data)
        return result

    async def get_count(self, session, dataset, signals, start_time, end_time):
        data = {
            "queries": [
                {
                    "dataset": dataset,
                    "signals": signals,
                    "interval": {
                        "start": ddt.format_datetime(start_time),
                        "end": ddt.format_datetime(end_time),
                    },
                    "aggregation": "count",
                }
            ]
        }
        result = await self.post(session, self.QUERY_POSTFIX, data)
        return result

    async def send_data(self, session, dataset_name, dataset):
        signals      = list(dataset.dataset.keys())
        df           = dataset.to_dataframe()
        samples      = []        
        times        = [ddt.format_datetime(time) for time in df.index]
        for index, row in df.iterrows():
            batch = []
            for signal in signals:
                batch.append(row[signal])
            samples.append(batch)

        # Don't bother sending if there is no data to send.
        if not samples:
            return
        
        data = {
            "inserts": [
                {
                    "dataset": dataset_name,
                    "signals": signals,
                    "samples": samples,
                    "times": times,
                }
            ]
        }

        return await self.post(session, self.INSERT_POSTFIX, data)

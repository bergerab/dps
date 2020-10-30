import json

import dps_services.util as ddt

from .util import *

class APIClient:
    def __init__(self, url):
        # Ensure URL ends with a slash
        if url[-1] != '/':
            url += '/'
        self.url = url

    async def get(self, session, postfix):
        resp = await session.get(self.url + postfix)
        return json.loads(await resp.text())

    async def post(self, session, postfix, data):
        resp = await session.post(self.url + postfix, json=data)
        return json.loads(await resp.text())

class DPSManagerAPIClient(APIClient):
    POP_JOB_POSTFIX  = 'api/v1/pop_job'
    RESULT_POSTFIX   = 'api/v1/result'
    PROGRESS_POSTFIX = 'api/v1/progress'
    
    async def send_result(self, session, batch_process_id, aggregations, complete):
        results = dict_to_mappings(aggregations)
        return await self.post(session, self.RESULT_POSTFIX, {
            'batch_process_id': batch_process_id,
            'results':          results,
            'complete':         complete,            
        })

    async def send_progress(self, session, batch_process_id, time, state):
        return await self.post(session, PROGRESS_POSTFIX, {
            'batch_process_id': batch_process_id,
            'time':             time,
            'state':            str(state),
        })

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
        return await self.post(session, self.QUERY_POSTFIX, data)

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

        return await self.post(session, self.INSERT_POSTFIX, {
            "inserts": [
                {
                    "dataset": dataset_name,
                    "signals": signals,
                    "samples": samples,
                    "times": times,
                }
            ]
        })

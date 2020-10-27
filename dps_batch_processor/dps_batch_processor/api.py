import json

class DPSMangerAPIClient:
    POP_JOB_POSTFIX  = '/api/v1/pop_job'
    RESULT_POSTFIX   = '/api/v1/result'
    PROGRESS_POSTFIX = '/api/v1/progress'
    
    def __init__(self, url):
        # Ensure URL ends with a slash
        if url[-1] != '/':
            url += '/'
        self.url = url

    async def send_result(self, session, batch_process_id, aggregations, complete):
        results = dict_to_mappings(aggregations)
        return self.post(session, RESULT_POSTFIX, {
            'batch_process_id': batch_process_id,
            'results':          results,
            'complete':         complete,            
        })

    async def send_progress(self, session, batch_process_id, time, state):
        return self.post(session, PROGRESS_POSTFIX, {
            'batch_process_id': batch_process_id,
            'time':             time,
            'state':            str(state),
        })

    async def pop_job(self, session):
        return self.get(session, POP_JOB_POSTFIX)

    async def get(self, session, postfix):
        async with session.get(url + postfix) as resp:
            return json.loads(await resp.text())

    async def post(self, session, postfix, data):
        async with session.post(url + postfix, json=data) as resp:
            return json.loads(await resp.text())


class DatabaseManagerAPIClient:
    '''
    An API client for a DPS Database Manager server.

    Ideally this wouldn't be necessary, and I would simply use DPS Client to send data.
    However, this program is written using asyncio, and requires asynchronous HTTP requests.
    '''
    POP_JOB_POSTFIX  = '/api/v1/pop_job'
    RESULT_POSTFIX   = '/api/v1/result'
    PROGRESS_POSTFIX = '/api/v1/progress'
    
    def __init__(self, url):
        # Ensure URL ends with a slash
        if url[-1] != '/':
            url += '/'
        self.url = url

    async def send_result(self, session, batch_process_id, aggregations, complete):
        results = dict_to_mappings(aggregations)
        return self.post(session, RESULT_POSTFIX, {
            'batch_process_id': batch_process_id,
            'results':          results,
            'complete':         complete,            
        })

    async def send_progress(self, session, batch_process_id, time, state):
        return self.post(session, PROGRESS_POSTFIX, {
            'batch_process_id': batch_process_id,
            'time':             time,
            'state':            str(state),
        })

    async def pop_job(self, session):
        return self.get(session, POP_JOB_POSTFIX)

    async def get(self, session, postfix):
        async with session.get(url + postfix) as resp:
            return json.loads(await resp.text())

    async def post(self, session, postfix, data):
        async with session.post(url + postfix, json=data) as resp:
            return json.loads(await resp.text())

import json
from datetime import datetime, timedelta

import asyncio
import aiohttp
import pandas as pd

from signal import SIGINT, SIGTERM

import dplib

INTERVAL = 10
'''
How many seconds to wait between checking for job.
'''

POP_JOB_URL = 'http://localhost:8000/api/v1/pop_job'

RESULT_URL = 'http://localhost:8000/api/v1/result'
PROGRESS_URL = 'http://localhost:8000/api/v1/progress'

async def main():
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(POP_JOB_URL) as resp:
                job = json.loads(await resp.text())
                if not job:
                    print('No jobs were available...')
                else:
                    print('Acquired a job.')
                    batch_process = job['batch_process']
                    system = batch_process['system']
                    component = dplib.Component('Temp')
                    for kpi in system['kpis']:
                        identifier = kpi['identifier']
                        if identifier == '':
                            identifier = None
                        component.add(kpi['name'], kpi['computation'], id=identifier)

                    mappings = { mapping['key']: mapping['value']
                                 for mapping in batch_process['mappings']}

                    parameters = []
                    for parameter in system['parameters']:
                        identifier = parameter['identifier'] or parameter['name']                        
                        if parameter['default']:
                            print('default', parameter['default'])

                            mappings[identifier] = dplib.DPL().compile(parameter['default']).run()
                        parameters.append(identifier)

                    print('DINk')

                    for key in mappings:
                        if key in parameters:
                            print(mappings[key])
                            mappings[key] = dplib.DPL().compile(mappings[key]).run()

                    print(mappings)
                    
                    bp = component.make_pruned_bp(batch_process['kpis'], mappings)

                    max_window = bp._get_max_window(mappings)

                    signals = []
                    for name in component.get_required_inputs(batch_process['kpis']):
                        if name not in parameters:
                            signals.append(name)

                    print(signals, max_window)
                    now = datetime.now()
                    data = {
                        'Time': map(lambda x: now + timedelta(seconds=x), range(1, 10))
                    }
                    for key in mappings:
                        if key in signals:
                            data[mappings[key]] = list(range(1, 10))
                    df = pd.DataFrame(data=data)
                    result = component.run(df, batch_process['kpis'], mappings)
                    print(result.get_aggregations())

        await asyncio.sleep(INTERVAL)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.add_signal_handler(SIGINT, main_task.cancel)
loop.add_signal_handler(SIGTERM, main_task.cancel)

import json
from datetime import datetime, timedelta

import asyncio
import aiohttp
import click
import pandas as pd

from signal import SIGINT, SIGTERM

import dplib

from .util import *

from dps_client import DPSClient

@click.command()
@click.option('--url',      required=True, help='The URL of the DPS manager.')
@click.option('--interval', default=5,     help='The number of seconds to wait between checking for jobs.')
@click.option('--verbose',                 help='Show the progress of jobs in the command line.')
def cli(url, interval=5, verbose=False):
    logger = Logger(verbose)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url, interval, logger))
    loop.add_signal_handler(SIGINT, main_task.cancel)
    loop.add_signal_handler(SIGTERM, main_task.cancel)

async def main(url, interval, logger):
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(POP_JOB_URL) as resp:
                job = json.loads(await resp.text())
                if not job:
                    logger.log('No jobs were available...')
                else:
                    logger.log('Acquired a job.')
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
                            mappings[identifier] = parameter['default']
                        parameters.append(identifier)

                    for key in mappings:
                        if key in parameters:
                            value = mappings[key]
                            mappings[key] = dplib.DPL().compile(value).run(mappings)
                    
                    bp = component.make_pruned_bp(batch_process['kpis'], mappings)

                    max_window = bp._get_max_window(mappings)

                    signals = []
                    for name in component.get_required_inputs(batch_process['kpis']):
                        if name not in parameters:
                            signals.append(name)

                    now = datetime.now()
                    data = {
                        'Time': map(lambda x: now + timedelta(seconds=x), range(1, 11))
                    }
                    for key in mappings:
                        if key in signals:
                            data[mappings[key]] = list(range(1, 11))
                    df = pd.DataFrame(data=data)

                    logger.log('final map', mappings)
                    result = component.run(df, batch_process['kpis'], mappings)
                    aggregations = result.get_aggregations()

                    results = []
                    for key in aggregations:
                        results.append({
                            'key': key,
                            'value': aggregations[key],
                        })
                    
                    async with session.post(RESULT_URL, json={
                            'batch_process_id': job['batch_process_id'],
                            'complete': True,
                            'results': results,
                    }) as resp:
                        logger.log('Sent results.')
                        print(await resp.text())

        await asyncio.sleep(interval)

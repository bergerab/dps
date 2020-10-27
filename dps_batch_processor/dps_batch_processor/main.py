import json
from datetime import datetime, timedelta

import asyncio
import aiohttp
import click
import pandas as pd

from signal import SIGINT, SIGTERM

import dplib

from .util import *
from .logger import Logger
from .api import DPSManagerAPIClient, DatabaseManagerAPIClient

DBM_URL = os.environ.get('DBM_URL')
if not DBM_URL:
    raise Exception('DPS Manager requires that you specify a `DBM_URL` environment variable. The value should be a URL to a DPS Database Manager.')
else:
    if not url_is_valid(DBM_URL):
        raise Exception('`DBM_URL` environment variable has an invalid URL value of "%s". Ensure the URL has a scheme (http:// or https://).' % DBM_URL)


@click.command()
@click.option('--dps_manager-url',      required=True,  help='The URL of the DPS Manager.')
@click.option('--database-manager-url', required=True,  help='The URL of the DPS Database Manager.')
@click.option('--polling-interval',     default=5,      help='The number of seconds to wait between checking for jobs.')
@click.option('--max-batch-size',       default=100000, help='The maximum number of datapoints to process in one batch.')
@click.option('--interval',             default=5,      help='The number of seconds to wait between checking for jobs.')
@click.option('--verbose',                              help='Show the progress of jobs in the command line.')
def cli(dps_manager_url, database_manager_url, max_batch_size, interval=5, verbose=False):
    if not url_is_valid(dps_manager_url):
        raise Exception(f'DPS Manager URL is invalid: "{dps_manager_url}". Ensure the URL is properly formatted and includes a scheme.')
    elif not url_is_valid(database_manager_url):
        raise Exception(f'DPS Database Manager URL is invalid: "{database_manager_url}". Ensure the URL is properly formatted and includes a scheme.')
    
    logger = Logger(verbose)
    loop = asyncio.get_event_loop()
    # `main` is written as a `asyncio` co-routine, so that if multiple batch processors
    # are supported (running multiple batch processes at once), this capability could be added,
    # by spawning another instance of the `main` co-routine.
    loop.run_until_complete(main(dps_manager_url, database_manager_url, max_batch_size, interval, logger))
    # Windows requires explicitly attaching signal handlers to
    # process signals for SIGINT/SIGTERM (for Ctrl-C to quit).
    loop.add_signal_handler(SIGINT, main_task.cancel)
    loop.add_signal_handler(SIGTERM, main_task.cancel)

async def main(dps_manager_url, database_manager_url, max_batch_size, interval=5, logger):
    api = DPSManagerAPIClient(url)
    while True:
        async with aiohttp.ClientSession() as session:
            async with api.pop_job(session) as job:
                if not job:
                    logger.log('No jobs were available.')
                else:
                    logger.log('Acquired a job.')
                    process_job(session, job)
        await asyncio.sleep(interval)

def process_job(session, job):
    # Extract values from response.
    batch_process    = job['batch_process']
    batch_process_id = job['batch_process_id']
    system           = batch_process['system']
    kpis             = batch_process['kpis']
    interval         = batch_process['interval']
    start_time       = interval['start']
    end_time         = interval['end']

    # Extract the signal/parameter mappings from the `batch_process`.
    # Then, evaluate the parameter strings as DPL (Python) source code
    # and yield a Python object (typically a number).
    mappings   = get_mappings(batch_process)
    parameters = get_system_parameters(system)
    evaluate_parameters(mappings, parameters)

    # Create a `dplib.Component` that can compute any KPI for the entire system.
    # Then using `component`, create a batch process that only computes the
    # KPIs in the job (assigned to `bp`).
    component = make_component(system)
    bp        = component.make_pruned_bp(kpis, mappings)

    # Get the identifiers of each signal who's data is required to run the batch process
    # Then, begin processing the data by fetching data from the Database Manager
    # in batches of `max_batch_size`.
    signals = get_signal_identifiers(component, batch_process, parameters)
    while dbm.hasdata():
        df = pd.DataFrame(data=data)

        # Run the batch process with 
        result       = component.run(df, kpis, mappings)
        aggregations = result.get_aggregations()

    # TODO: write the intermediate results to the database using the batch process ID.

    async with api.send_result(session,
                               batch_process_id,
                               aggregations,
                               True) as resp:
        logger.log('Sent results.')
        print(resp)

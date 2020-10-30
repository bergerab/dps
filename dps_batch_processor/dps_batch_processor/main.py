import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

import asyncio
import aiohttp
import click
import pandas as pd

from signal import SIGINT, SIGTERM

import dplib
import dps_services.util as ddt

from .util import *
from .logger import Logger
from .api import DPSManagerAPIClient, DatabaseManagerAPIClient

@click.command()
@click.option('--dps-manager-url',      required=True,  help='The URL of the DPS Manager.')
@click.option('--database-manager-url', required=True,  help='The URL of the DPS Database Manager.')
@click.option('--polling-interval',     default=5,      help='The number of seconds to wait between checking for jobs.')
@click.option('--max-batch-size',       default=100000, help='The maximum number of datapoints to process in one batch.')
@click.option('--interval',             default=5,      help='The number of seconds to wait between checking for jobs.')
@click.option('--verbose',                              help='Show the progress of jobs in the command line.')
def cli(dps_manager_url, database_manager_url, polling_interval, max_batch_size, interval=5, verbose=False):
    if not url_is_valid(dps_manager_url):
        raise Exception(f'DPS Manager URL is invalid: "{dps_manager_url}". Ensure the URL is properly formatted and includes a scheme.')
    elif not url_is_valid(database_manager_url):
        raise Exception(f'DPS Database Manager URL is invalid: "{database_manager_url}". Ensure the URL is properly formatted and includes a scheme.')
    
    logger = Logger(verbose)
    loop = asyncio.get_event_loop()
    # `main` is written as a `asyncio` co-routine, so that if multiple batch processors
    # are supported (running multiple batch processes at once), this capability could be added,
    # by spawning another instance of the `main` co-routine.
    loop.run_until_complete(main(dps_manager_url, database_manager_url, max_batch_size, logger, interval))
    # Windows requires explicitly attaching signal handlers to
    # process signals for SIGINT/SIGTERM (for Ctrl-C to quit).
    loop.add_signal_handler(SIGINT, main_task.cancel)
    loop.add_signal_handler(SIGTERM, main_task.cancel)

async def main(dps_manager_url, database_manager_url, max_batch_size, logger, interval=5):
    api = DPSManagerAPIClient(dps_manager_url)
    while True:
        async with aiohttp.ClientSession() as session:
            job = await api.pop_job(session)
            if not job:
                logger.log('No jobs were available.')
            else:
                logger.log('Acquired a job.')
                await process_job(api, logger, session, job,
                                  DatabaseManagerAPIClient(database_manager_url),
                                  max_batch_size)
        await asyncio.sleep(interval)

async def process_job(api, logger, session, job, dbc, max_batch_size):
    # Extract values from response.
    batch_process    = job['batch_process']
    batch_process_id = job['batch_process_id']
    system           = batch_process['system']
    kpis             = batch_process['kpis']
    interval         = batch_process['interval']
    start_time       = ddt.parse_datetime(interval['start'])
    end_time         = ddt.parse_datetime(interval['end'])

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
    signals            = get_signal_identifiers(component, batch_process, parameters)
    max_window         = bp._get_max_window(mappings)
    current_start_time = start_time
    dbm_has_data       = True
    samples            = []
    times              = []
    result             = None
    while dbm_has_data:
        data = await dbc.get_data(session, '', signals,
                     current_start_time, end_time,
                     limit=max_batch_size)
        if 'results' not in data:
            print(data)
        results = data['results'][0]
        samples += results['samples']
        times   += [ddt.parse_datetime(time) for time in results['times']]

        # If there is no more data after this, end the process after this batch completes.
        if len(signals) * len(samples) < max_batch_size:
            dbm_has_data = False
        else:
            # Start the next batch of data at the last time we got from this batch.
            # Don't use that batch's sample data because there is a chance the samples
            # could be missing if the limit is not a multiple of the # of signals.
            samples.pop()
            current_start_time = times.pop()

        # If the computation contains a window,
        # and if we have not accumulated enough data to fill the largest window,
        # continue collecting data into the `samples` and `times` variables.
        if max_window is not None:
            delta_time = times[-1] - times[0]
            if delta_time < max_window:
                continue

        # Split data into chunks of size `max_window`
        series = dplib.Series(samples, times)

        # If the computation contains a window, window the data based on the max window size.
        # Otherwise, create a dummy window with just one item.
        if max_window is not None:
            windowed_series = list(series.window(max_window))
            # If there is more data after this batch, use the last window in the next batch.
            # This prevents a batch which ends on an odd number from happening. For example,
            # at the end of the batch, if the batch's size is not the same as the window's.
            # This should be tolerated at the very end of a batch process, but not in between
            # batches.
            if dbm_has_data:
                last_series = windowed_series.pop()
                times   = list(last_series.index)
                samples = list(last_series)
            else:
                times   = []
                samples = []
        else:
            windowed_series = [series.series] # Extract the pandas series from the `dp.Series`
            times   = []
            samples = []
        
        # Convert the response from the Database Manager server into a `pd.DataFrame`.
        for window in windowed_series:
            df_data = defaultdict(list)
            for batch in window:
                for i, signal in enumerate(signals):
                    df_data[signal].append(batch[i])

            # Create a DataFrame `df` based on the data in the window.
            # Then, run the batch process with the DataFrame `df`.
            df           = pd.DataFrame(data=df_data, index=window.index)
            logger.log('Processing DataFrame:\n', df)
            result       = component.run(df, kpis, mappings, previous_result=result)
            values       = result.get_intermidiate_values()
            aggregations = result.get_aggregations()
            logger.log('Aggregations', aggregations)

            # Send the intermediate results to the database.
            logger.log('Sending intermediate results.')                                    
            resp = await dbc.send_data(session, 'batch_process' + str(batch_process_id), values)
            logger.log(resp)                        
            resp = await api.send_result(session,
                                         batch_process_id,
                                         result.get_aggregations(),
                                         False)
            logger.log(resp)
            
            

    # TODO: write the intermediate results to the database using the batch process ID.
    
    resp = await api.send_result(session,
                          batch_process_id,
                          result.get_aggregations(),
                          True)
    logger.log('Finished processing job.')
    logger.log(resp)

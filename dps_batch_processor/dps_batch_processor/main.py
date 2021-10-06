import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import traceback

import asyncio
import aiohttp
import click
import pandas as pd

from signal import SIGINT, SIGTERM

import dplib
import dps_services.util as ddt

from .util import *
from .logger import Logger
from .api import DPSManagerAPIClient, \
    DatabaseManagerAPIClient, \
    STATUS_ERROR, \
    STATUS_RUNNING, \
    STATUS_COMPLETE

exceptions = (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ClientOSError)

@click.command()
@click.option('--dps-manager-url',      required=True,  help='The URL of the DPS Manager.')
@click.option('--database-manager-url', required=True,  help='The URL of the DPS Database Manager.')
@click.option('--api-key',              required=True,  help='The API key to use.')
@click.option('--polling-interval',     default=5,      help='The number of seconds to wait between checking for jobs.')
@click.option('--max-batch-size',       default=10000, help='The maximum number of datapoints to process in one batch.')
@click.option('--interval',             default=5,      help='The number of seconds to wait between checking for jobs.')
@click.option('--verbose',                              help='Show the progress of jobs in the command line.')
def cli(dps_manager_url, database_manager_url, api_key, polling_interval, max_batch_size, interval=5, verbose=False):
    do_cli(*args, **kwargs)

def do_cli(dps_manager_url, database_manager_url, api_key, polling_interval, max_batch_size, interval=5, verbose=False):    
    logger = Logger(verbose)
    loop = asyncio.get_event_loop()

    # `main` is written as a `asyncio` co-routine, so that if multiple batch processors
    # are supported (running multiple batch processes at once), this capability could be added,
    # by spawning another instance of the `main` co-routine.
    loop.run_until_complete(main(dps_manager_url, database_manager_url, api_key, max_batch_size, logger, interval))
    # Windows requires explicitly attaching signal handlers to
    # process signals for SIGINT/SIGTERM (for Ctrl-C to quit).
    loop.add_signal_handler(SIGINT, main_task.cancel)
    loop.add_signal_handler(SIGTERM, main_task.cancel)
    return loop

async def main(dps_manager_url, database_manager_url, api_key, max_batch_size, logger, interval=5):
    api = DPSManagerAPIClient(dps_manager_url, api_key)
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                job = await api.pop_job(session)
                if not job:
                    logger.log('No jobs were available.')
                elif job == 403:
                    logger.error('Failed fetching jobs due to an invalid API key.')
                else:
                    logger.log('Acquired a job.')
                    await process_job(api, logger, session, job,
                                      DatabaseManagerAPIClient(database_manager_url, api_key),
                                      max_batch_size)
            except exceptions:
                logger.error('Failed connecting to DPS Manager server.')
        await asyncio.sleep(interval)

async def process_job(api, logger, session, job, dbc, max_batch_size):
    async def handle_unexpected_exception():
        await send_error(f'{e}\n\nStack trace:\n {traceback.format_exc()}', logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)
        logger.log(f'Sent error that occured during batch process:  {e}\n\nStack trace:\n {traceback.format_exc()}')
    # Extract values from response.
    batch_process    = job['batch_process']
    batch_process_id = job['batch_process_id']
    system           = batch_process['system']
    kpis             = batch_process['kpis']
    interval         = batch_process['interval']
    dataset          = batch_process['dataset']
    start_time       = ddt.parse_datetime(interval['start'])
    end_time         = ddt.parse_datetime(interval['end'])
    use_date_range   = batch_process['use_date_range']
    frame_counter   = 0 # how many frames of samples have we seen

    # Extract the signal/parameter mappings from the `batch_process`.
    # Then, evaluate the parameter strings as DPL (Python) source code
    # and yield a Python object (typically a number).
    mappings   = get_mappings(batch_process) # Gets the signal names in the mapping
    parameters = get_system_parameters(system)
    mapped_signals = [value for id, value in mappings.items() if id not in parameters]
    logger.log('Evaluating parameters...')    
    evaluate_parameters(mappings, parameters)

    # Create a `dplib.Component` that can compute any KPI for the entire system.
    # Then using `component`, create a batch process that only computes the
    # KPIs in the job (assigned to `bp`).
    component = make_component(system)
    logger.log('Initializing batch process...')
    bp        = component.make_pruned_bp(kpis, mappings)

    # Get the identifiers of each signal who's data is required to run the batch process
    # Then, begin processing the data by fetching data from the Database Manager
    # in batches of `max_batch_size`.
    signals            = get_signal_identifiers(component, batch_process, parameters)
    max_window         = bp._get_max_window(mappings)
    dbm_has_data       = True
    samples            = []
    times              = []
    result             = None
    inter_results      = dp.Dataset() # Intermediate results
    chartables         = set() # Keep track of which signals are plottable on a chart
    total_samples      = 0 # A counter to keep track of the number of samples to process    
    processed_samples  = 0 # A counter to keep track of the number of samples that we have processed

    if not use_date_range:
        try:
            logger.log('Getting range (because no date range was specified).')
            logger.log('Determining interval for dataset... All signals in the dataset: ')
            logger.log(mapped_signals)
            resp = await dbc.get_dataset_range(session, dataset)

            if 'results' not in resp:
                await send_error(f'Dataset {dataset} has no samples. Try the batch process again after adding data, or select a different dataset.',
                                 logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)
                        
            start_time = ddt.parse_datetime(resp['results'][0]['first'])
            end_time = ddt.parse_datetime(resp['results'][0]['last'])

            logger.log(f'Found longest interval of {start_time} to {end_time}.')
        except exceptions:
            await send_error("Failed to connect to DPS Database Manager server when getting sample count.",
                             logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)
            logger.log(f'Sent error that occured when getting sample count from Database Manager.')
            return
        except Exception as e:
            await handle_unexpected_exception();
            return;

    # set below the use_date_range check, because start_time may have been updated
    current_start_time = start_time

    try:
        logger.log('Getting sample count.')
        data = await dbc.get_count(session, dataset, mapped_signals, current_start_time, end_time)
    except exceptions:
        await send_error("Failed to connect to DPS Database Manager server when getting sample count.",
                         logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)

        logger.log(f'Sent error that occured when getting sample count from Database Manager.')
        return
    except Exception as e:
        await handle_unexpected_exception()
        return

    if 'results' in data:
        total_samples = sum(data['results'][0]['values'])
        logger.log(f'Got total samples (was {total_samples}).')

    else:
        await send_error(str(data['error'][-1]),
                         logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)

        logger.log(f'Sent error that occured when getting sample count from Database Manager.')
        return 

    temp_result = await send_result(STATUS_RUNNING, 
                                    logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)

    if temp_result == 404: 
        return

    result_id = temp_result['result_id']

    if total_samples == 0:
        await send_result(STATUS_COMPLETE, 
                          logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)
        logger.log('Ending batch process, as there are no input samples.')
        return

    while dbm_has_data:
        try:
            data = await dbc.get_data(session, dataset, mapped_signals,
                                      current_start_time, end_time,
                                      limit=max_batch_size)
        except exceptions:            
            await send_error("Failed to connect to DPS Database Manager server when sending results.",
                             logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)
            return
        except Exception as e:
            await handle_unexpected_exception()
            return
        # If no results are returned, print it as an error and return.
        if 'results' not in data:
            logger.error(data)
            return
        results = data['results'][0]
        samples += results['samples']
        times   += [ddt.parse_datetime(time) for time in results['times']]
        
        processed_samples += len(results['samples']) * len(signals)

        # If there is no more data after this, end the process after this batch completes.
        if len(signals) * len(samples) < max_batch_size:
            dbm_has_data = False
        else:
            # Start the next batch of data at the last time we got from this batch.
            # Don't use that batch's sample data because there is a chance the samples
            # could be missing if the limit is not a multiple of the # of signals.
            samples.pop()
            current_start_time = times.pop()
            processed_samples -= len(signals)

        # If the computation contains a window,
        # and if we have not accumulated enough data to fill the largest window,
        # continue collecting data into the `samples` and `times` variables.
        #
        # There is also a check to make sure if there is more data to accumulate.
        # If there is no more data to accumulate, we should finish processing that data
        # otherwise, we would continuously ask for more data.
        if max_window is not None and dbm_has_data:
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
                for i, signal in enumerate(mapped_signals):
                    df_data[signal].append(batch[i])

            # Create a DataFrame `df` based on the data in the window.
            # Then, run the batch process with the DataFrame `df`.
            df           = pd.DataFrame(data=df_data, index=window.index)
            logger.log('Processing DataFrame:\n', df)
            
            try:
                print('mappings', mappings)
                next_result       = component.run(df, kpis, mappings, previous_result=result, additional_builtins={ 'GET_FRAME_COUNT': lambda: frame_counter })
                if result:
                    next_result.aggregations = result.get_merged_aggregations(next_result)
                result = next_result

                # After every batch is run, send the intermediate results
                inter_results = inter_results.merge(result.get_intermidiate_values())

                aggregations = result.get_aggregations()
                logger.log('Aggregations for this step: ', aggregations)

                for batch in window:
                    frame_counter += len(batch)
                logger.log('Updated frame counter: ', frame_counter)
            except Exception as e:
                # Send the error message to the server.
                await send_error(f'Error occured when running KPI computation: {e}\n\nStack trace:\n {traceback.format_exc()}',
                           logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)
                return

        chartables = chartables.union(set(inter_results.dataset.keys()))

        ires = await flush_inter_results(api, logger, dbc, session, batch_process_id, inter_results, chartables, result, result_id, processed_samples, total_samples)
        if ires == 404: 
            await send_error(f'Failed to send intermediate results to DPS Database Manager',
                       logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)
            return

        inter_results = dp.Dataset()

    # Write any remaining intermediate results
    await flush_inter_results(api, logger, dbc, session, batch_process_id, inter_results, chartables, result, result_id, processed_samples, total_samples)

    await send_result(STATUS_COMPLETE, 
                      logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)

    logger.log('Finished processing job.')

async def flush_inter_results(api, logger, dbc, session, batch_process_id, inter_results, chartables, result, result_id, processed_samples, total_samples):
    try:
        logger.log('Sending intermediate results.')        
        resp = await dbc.send_data(session, 'batch_process' + str(batch_process_id), inter_results)
        logger.log(resp)
    except exceptions:                                                        
        await send_error("Failed to connect to DPS Database Manager server when sending intermediate results.",
                         logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)
    except Exception as e:
        await send_error(e, logger, api, session, batch_process_id, result, inter_results, chartables, None, processed_samples, total_samples)
        logger.log(f'Sent error that occured during batch process: {e}')
        return

    resp = await send_result(STATUS_RUNNING, 
                             logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples)

    return resp

async def send_error(message, logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples):
    try:
        resp = await api.send_result(session,
                                     batch_process_id,
                                     result.get_aggregations() if result is not None else {},
                                     inter_results,
                                     chartables,
                                     STATUS_ERROR,
                                     result_id=result_id,
                                     message=str(message),
                                     processed_samples=processed_samples,
                                     total_samples=total_samples)

        if resp == 404:
            logger.log('Batch process was cancelled.')

    except Exception as e:
        print('Failed to send error to DPS Manager. Reason: ' + str(e))
        resp = 404

    logger.log(resp)
    
async def send_result(status, logger, api, session, batch_process_id, result, inter_results, chartables, result_id, processed_samples, total_samples):
    try:
        resp = await api.send_result(session,
                                     batch_process_id,
                                     result.get_aggregations() if result is not None else {},
                                     inter_results,
                                     chartables,
                                     status,
                                     result_id=result_id,
                                     processed_samples=processed_samples,
                                     total_samples=total_samples)

        if resp == 404:
            logger.log('Batch process was cancelled.')

    except Exception as e:
        logger.error('Failed to send result to DPS Manager. Reason: ' + str(e))
        resp = 404

    logger.log(resp)
    return resp

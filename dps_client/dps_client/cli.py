import sys
from .main import Client

from datetime import datetime, timedelta
import requests

import click

@click.command()
@click.option('--input',       required=False, help='A filepath to the input file to use.')
@click.option('--dbm-url',     required=True, help='The URL of a DPS Database Manager.')
@click.option('--dataset',     required=True, help='The name of the dataset to upload the data to.')
@click.option('--api-key',     required=True, help='The API key to use.')
@click.option('--delete-dataset', default=False, help='Instead of inserting data, delete all data that is in the dataset.')
@click.option('--time-column',         default='Time', help='The name of the column that stores a relative time (delta time from beginning of data collection).')
@click.option('--start-time',         default=None, help='The start time in ISO format (e.g. 2021-01-01 00:00:00-06:00)')
@click.option('--absolute-time',         default=False, help='If the input file has absolute times in it.')
@click.option('--time-offset',         default=3600, help='The offset (in seconds) to derive an absolute timestamp. The first sample in the data has a derived timestamp that is the current time minus the time offset plus the data\'s time column (this process continues for the entire file).')
@click.option('--verbose',             default=True, help='Whether or not to print progress of the upload.')
@click.option('--include-time-column', default=False, help='Whether or not to include the time column as a signal.')
def cli(input, dbm_url, dataset, api_key, delete_dataset, time_column, start_time, absolute_time, time_offset, verbose, include_time_column):
    if not delete_dataset and not input:
        print('You must specify an input file with --input.')
        sys.exit()
    client = Client(dbm_url, dataset, api_key)
    
    if delete_dataset:
        requests.post('') # TODO, also add absolute start time
    else:
        if start_time == None: 
            if not absolute_time:
                start_time=datetime.utcnow() - timedelta(seconds=time_offset) 
        else: 
            start_time=datetime.fromisoformat(start_time)

        client.send_csv(input,
                        time_column=time_column, 
                        start_time=start_time,
                        verbose=verbose, 
                        include_time_column=include_time_column,
                        absolute_time=absolute_time)

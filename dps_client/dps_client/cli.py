import sys
from .main import Client

from datetime import datetime, timedelta
import requests

import click

@click.command()
@click.option('--input',       required=False, help='A filepath to the input file to use.')
@click.option('--dbm-url',     required=True, help='The URL of a DPS Database Manager.')
@click.option('--dataset',     required=True, help='The name of the dataset to upload the data to.')
@click.option('--delete-dataset', default=False, help='Instead of inserting data, delete all data that is in the dataset.')
@click.option('--time-column',         default='Time', help='The name of the column that stores a relative time (delta time from beginning of data collection).')
@click.option('--time-offset',         default=3600, help='The offset (in seconds) to derive an absolute timestamp. The first sample in the data has a derived timestamp that is the current time minus the time offset plus the data\'s time column (this process continues for the entire file).')
@click.option('--verbose',             default=True, help='Whether or not to print progress of the upload.')
@click.option('--include-time-column', default=False, help='Whether or not to include the time column as a signal.')
def cli(input, dbm_url, dataset, delete_dataset, time_column, time_offset, verbose, include_time_column):
    if not delete_dataset and not input:
        print('You must specify an input file with --input.')
        sys.exit()
    client = Client(dbm_url, dataset)

    if delete_dataset:
        requests.post('') # TODO
    else:
        client.send_csv(input,
                        time_column=time_column, 
                        start_time=datetime.utcnow() - timedelta(seconds=time_offset),
                        verbose=verbose, include_time_column=include_time_column)

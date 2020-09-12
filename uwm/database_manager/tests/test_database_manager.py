import requests

from unittest import TestCase
from datetime import datetime, timedelta

TEST_DATASET_NAME = 'test_dataset'

URL = 'http://localhost:3001/api/v1/'

def make_api_url(endpoint):
    return URL + endpoint

def post(endpoint, jo):
    try:
        response = requests.post(make_api_url(endpoint), json=jo)
    except requests.exceptions.ConnectionError:
        raise Exception(f'Server is down. These are integration tests and they require running the database manager server at {URL}.')        
    validate_response(response)
    return response

def validate_response(response):
    status_code = response.status_code
    if status_code is not 200:
        raise Exception(f'Invalid response ({response.status_code}):\n' + '\n'.join(response.json()['error']))

def clear(dataset_name):
    post('clear', {
        'dataset_name': dataset_name,
    })

def fetch(dataset_name, signal_names, interval_start, interval_end):
    return post('query', {
        'queries': [
            {
                'dataset': dataset_name,
                'signals': signal_names,
                'interval': {
                    'start': interval_start,
                    'end': interval_end,
                },
            }
        ]
    })

def aggregate(dataset_name, signal_names, interval_start, interval_end, aggregation):
    return post('query', {
        'queries': [
            {
                'dataset': dataset_name,
                'signals': signal_names,
                'interval': {
                    'start': interval_start,
                    'end': interval_end,
                },
                'aggregation': aggregation,
            }
        ]
    })

def insert(dataset_name):
    return post('insert', {
        'inserts': [
            {
                'dataset': dataset_name,
                
            }
        ]
    })


class TestDataSeries(TestCase):
    def test_query_empty(self):
        clear()

def send_query():
    return requests.post(URL + 'query', json={
        'queries': [
            {
                'dataset': 'test',
                'signals': ['Va', 'Vb', 'Vc'],
                'interval': {
                    'start': 1,
                    'end': 1000000000,
                }
            }
        ]
    })

def send_insert():
    return requests.post(URL + 'insert', json={
        'inserts': [
            {
                'dataset': 'test',
                'signals': ['Va', 'Vb', 'Vc'],
                'samples': [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                'times': [
                    str(datetime.utcnow() + timedelta(microseconds=0)),
                    str(datetime.utcnow() + timedelta(microseconds=1)),
                    str(datetime.utcnow() + timedelta(microseconds=2)),
                ],
            }
        ]
    })

from datetime import datetime, timedelta

import requests

URL = 'http://localhost:5000/api/v1/'

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

if __name__ == '__main__':
    resp = send_insert().json()
    
    if 'error' in resp:
        for error in resp['error']:
            print(error)

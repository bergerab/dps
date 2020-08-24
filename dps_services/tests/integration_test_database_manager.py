import requests

URL = 'http://localhost:5000/api/v1/'


def send_query():
    requests.post(URL + 'query', json={
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

print(send_query())

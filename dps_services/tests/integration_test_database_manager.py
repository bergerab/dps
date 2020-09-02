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
                'times': [3, 4, 5, 6],
            }
        ]
    })

print(send_insert().json())

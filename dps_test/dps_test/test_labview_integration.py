from datetime import datetime, timedelta
from time import sleep
import requests
import unittest

def make_test_case(url, dbm_client, send_threshold):
    def delete_dataset(dataset_name):
        return dbm_client.POST('delete_dataset', {
            'dataset': dataset_name,
        })
    
    DATETIME_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%f'
    def query(dataset_name, signal_names):
        d = {
            'queries': [
                {
                    'dataset': dataset_name,
                    'signals': signal_names,
                    'interval': {
                        'start': datetime.strftime(datetime.utcnow() - timedelta(seconds=1), DATETIME_FORMAT_STRING),
                        'end': datetime.strftime(datetime.utcnow() + timedelta(seconds=1), DATETIME_FORMAT_STRING),
                    },
                }
            ]
        }
        return dbm_client.POST('query', d)

    DS1 = 'test_dataset1'
    DS2 = 'test_dataset2'

    ingest_url = url + '/ingest'
    
    class TestLabVIEWIntegration(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super(TestLabVIEWIntegration, self).__init__(*args, **kwargs)        
            self.maxDiff = None

        def test_send(self):
            for i in range(send_threshold):
                requests.post(ingest_url, data=f'{DS1};va;{i};vb;{i+1};vc;{i+2}')

            result = query(DS1, ['va', 'vb', 'vc']).json()['results'][0]

            # Ensure all the times are (somewhat) accurate
            self.assertEqual(len(result['times']), send_threshold)
            for time_string in result['times']:
                t = datetime.strptime(time_string, DATETIME_FORMAT_STRING)                
                self.assertLess(t, datetime.utcnow())
                self.assertGreater(t, datetime.utcnow() - timedelta(seconds=1))

            # Ensure all samples are the same
            for i, batch in enumerate(result['samples']):
                self.assertEqual(batch, [i + j for j in range(3)])

    return TestLabVIEWIntegration

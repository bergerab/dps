from datetime import datetime
import unittest

def make_test_case(client):
    def insert(dataset, signal_names, samples, times):
        return client.POST('insert', {
            'inserts': [
                {
                    'dataset': dataset,
                    'signals': signal_names,
                    'samples': samples,
                    'times': times,
                }
            ]
        })

    def delete_dataset(dataset_name):
        return client.POST('delete_dataset', {
            'dataset': dataset_name,
        })

    def query(dataset_name, signal_names, interval_start, interval_end):
        return client.POST('query', {
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

    DS1 = 'test_dataset1'
    DS2 = 'test_dataset2'

    datetime_string1 = '2020-06-30 03:54:45.175489'
    datetime1 = datetime(2020, 6, 30, 3, 54, 45, 175489)
    datetime_string2 = '2021-07-12 10:37:19.839234'
    datetime2 = datetime(2021, 7, 12, 10, 37, 19, 839234)
    datetime_string3 = '2023-10-06 14:00:02.002'
    datetime3 = datetime(2023, 10, 6, 14, 0, 2, 2000)
    datetime_string4 = '2023-10-06 15:02:12.000392'
    datetime4 = datetime(2023, 10, 6, 15, 2, 12, 392)
    datetime_string5 = '2023-10-06 16:07:08.001811'
    datetime5 = datetime(2023, 10, 6, 16, 7, 8, 1811)
    
    class TestDatabaseManager(unittest.TestCase):
        def test_insert(self):
            delete_response = delete_dataset(DS1)
            self.assertEqual(delete_response.status_code, 200)            
            self.assertEqual(delete_response.json(), {
                'message': 'OK',
            })
            insert_response = insert(DS1, ['va', 'vb', 'vc'], [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [datetime_string2, datetime_string3])
            self.assertEqual(insert_response.status_code, 200)                        
            self.assertEqual(insert_response.json(), {
                'message': 'OK',
            })
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4)
            self.assertEqual(query_response.status_code, 200)
            self.maxDiff = None
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'signals': ['va', 'vb', 'vc'],
                        'times': [datetime2, datetime3],
                        'samples': [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime2,
                                'end': datetime3,
                            },
                            'signals': ['va', 'vb', 'vc'],
                        }
                    }
                ]
            })

    return TestDatabaseManager

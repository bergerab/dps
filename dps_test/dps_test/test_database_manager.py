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

    def query(dataset_name, signal_names, interval_start, interval_end, aggregation=None, limit=None):
        d = {
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
        }
        if aggregation:
            d['queries'][0]['aggregation'] = aggregation
        if limit:
            d['queries'][0]['limit'] = limit
        return client.POST('query', d)

    DS1 = 'test_dataset1'
    DS2 = 'test_dataset2'

    datetime_string1 = '2020-06-30 03:54:45.175489'
    datetime1 = datetime(2020, 6, 30, 3, 54, 45, 175489)
    datetime_string2 = '2021-07-12 10:37:19.839234'
    datetime2 = datetime(2021, 7, 12, 10, 37, 19, 839234)
    datetime_string3 = '2023-10-06 14:00:02.002000'
    datetime3 = datetime(2023, 10, 6, 14, 0, 2, 2000)
    datetime_string4 = '2023-10-06 15:02:12.000392'
    datetime4 = datetime(2023, 10, 6, 15, 2, 12, 392)
    datetime_string5 = '2023-10-06 16:07:08.001811'
    datetime5 = datetime(2023, 10, 6, 16, 7, 8, 1811)
    
    class TestDatabaseManager(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super(TestDatabaseManager, self).__init__(*args, **kwargs)        
            self.maxDiff = None
        
        def validate_status_code(self, response):
            if response.status_code != 200:
                print(response.json())
            self.assertEqual(response.status_code, 200)

        def delete_dataset(self, dataset_name):
            delete_response = delete_dataset(dataset_name)
            self.validate_status_code(delete_response)
            self.assertEqual(delete_response.json(), {
                'message': 'OK',
            })
        
        def test_insert_then_query(self):
            self.delete_dataset(DS1)
            
            insert_response = insert(DS1, ['va', 'vb', 'vc'], [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [datetime_string2, datetime_string3])
            self.validate_status_code(insert_response)            
            self.assertEqual(insert_response.json(), {
                'message': 'OK',
            })
            
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4)
            self.validate_status_code(query_response)                        
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'times': [datetime_string2, datetime_string3],
                        'samples': [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['va', 'vb', 'vc'],
                        }
                    }
                ]
            })

            # Test limit
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4, limit=5)
            self.validate_status_code(query_response)                        
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'times': [datetime_string2, datetime_string3],
                        'samples': [[1.0, 2.0, 3.0], [0, 5.0, 6.0]],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['va', 'vb', 'vc'],
                            'limit': 5,
                        }
                    }
                ]
            })

            # Test limit
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4, limit=5)
            self.validate_status_code(query_response)
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'times': [datetime_string2, datetime_string3],
                        'samples': [[1.0, 2.0, 3.0], [0, 5.0, 6.0]],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['va', 'vb', 'vc'],
                            'limit': 5,
                        }
                    }
                ]
            })

            # TODO: There is some weird bug if the limit is 4 where the last sample doesn't show up. This won't
            # be a problem in our system, because we drop the last sample after every request in the
            # DPS batch processor.
            
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4, limit=3)
            self.validate_status_code(query_response)                        
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'times': [datetime_string2],
                        'samples': [[1.0, 2.0, 3.0]],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['va', 'vb', 'vc'],
                            'limit': 3,
                        }
                    }
                ]
            })
            
            self.delete_dataset(DS1)

        def test_multiple_inserts(self):
            self.delete_dataset(DS1)
            
            insert_response = insert(DS1, ['va', 'vb', 'vc'], [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [datetime_string2, datetime_string3])
            self.validate_status_code(insert_response)                                                
            self.assertEqual(insert_response.json(), {
                'message': 'OK',
            })
            
            insert_response = insert(DS1, ['sig1', 'sig2'], [[3.2, 9.324], [4.293, 3.21], [5.3, 2.1], [0.32, 3.11]],
                                     [datetime_string1, datetime_string2, datetime_string3, datetime_string4])
            self.validate_status_code(insert_response)                                                            
            self.assertEqual(insert_response.json(), {
                'message': 'OK',
            })
            
            query_response = query(DS1, ['va', 'vb', 'sig1', 'sig2'], datetime_string2, datetime_string5)
            self.validate_status_code(query_response)                                                                        
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'times': [datetime_string2, datetime_string3, datetime_string4],
                        'samples': [[1.0, 2.0, 4.293, 3.21], [4.0, 5.0, 5.3, 2.1], [0.0, 0.0, 0.32, 3.11]],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string2,
                                'end': datetime_string5,
                            },
                            'signals': ['va', 'vb', 'sig1', 'sig2'],
                        }
                    }
                ]
            })

            self.delete_dataset(DS1)

        def test_aggregation(self):
            self.delete_dataset(DS1)
            
            insert_response = insert(DS1, ['va', 'vb', 'vc'], [[1.0, 12.0, 3.0], [4.0, 5.0, 6.0]], [datetime_string2, datetime_string3])
            self.validate_status_code(insert_response)                                                                                    
            self.assertEqual(insert_response.json(), {
                'message': 'OK',
            })

            # Test max aggregation
            query_response = query(DS1, ['va', 'vb'], datetime_string2, datetime_string5, aggregation='max')
            self.validate_status_code(query_response)                                                                                                
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'values': [4.0, 12.0],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string2,
                                'end': datetime_string5,
                            },
                            'signals': ['va', 'vb'],
                            'aggregation': 'max',
                        }
                    }
                ]
            })

            # Test min aggregation
            query_response = query(DS1, ['vc'], datetime_string1, datetime_string4, aggregation='min')
            self.validate_status_code(query_response)                                                                                                            
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'values': [3.0],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['vc'],
                            'aggregation': 'min',
                        }
                    }
                ]
            })

            # Test count aggregation
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4, aggregation='count')
            self.validate_status_code(query_response)                                                                                                                        
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'values': [2, 2, 2],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['va', 'vb', 'vc'],
                            'aggregation': 'count',
                        }
                    }
                ]
            })

            # Test average aggregation
            query_response = query(DS1, ['va', 'vb', 'vc'], datetime_string1, datetime_string4, aggregation='average')
            self.validate_status_code(query_response)
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'values': [(1.0 + 4.0) / 2, (12.0 + 5.0) / 2, (3.0 + 6.0) / 2],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string4,
                            },
                            'signals': ['va', 'vb', 'vc'],
                            'aggregation': 'average',
                        }
                    }
                ]
            })

            # Test max aggregation with filter
            query_response = query(DS1, ['vc'], datetime_string2, datetime_string2, aggregation='max')
            self.validate_status_code(query_response)            
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'values': [3.0],
                        'query': {
                            'dataset': DS1,
                            'interval': {
                                'start': datetime_string2,
                                'end': datetime_string2,
                            },
                            'signals': ['vc'],
                            'aggregation': 'max',
                        }
                    }
                ]
            })

            self.delete_dataset(DS1)

        def test_large_dataset(self):
            self.delete_dataset(DS2)

            ds1_samples = [[1.0, 12.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
            insert_response = insert(DS2, ['va', 'vb', 'vc'], ds1_samples, [datetime_string2, datetime_string3, datetime_string4])
            self.validate_status_code(insert_response)                                    
            self.assertEqual(insert_response.json(), {
                'message': 'OK',
            })

            query_response = query(DS2, ['va', 'vb', 'vc'], datetime_string1, datetime_string5)
            self.validate_status_code(query_response)                                                            
            self.assertEqual(query_response.json(), {
                'results': [
                    {
                        'times': [datetime_string2, datetime_string3, datetime_string4],
                        'samples': ds1_samples,
                        'query': {
                            'dataset': DS2,
                            'interval': {
                                'start': datetime_string1,
                                'end': datetime_string5,
                            },
                            'signals': ['va', 'vb', 'vc'],
                        }
                    }
                ]
            })

            self.delete_dataset(DS2)

    return TestDatabaseManager

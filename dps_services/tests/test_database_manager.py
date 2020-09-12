from unittest import TestCase
from datetime import datetime, timedelta

import dps_services.database_manager as dbm
import dps_services.util as util

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

class MockDataStore(dbm.DataStore):
    def __init__(self):
        self.queries = []
        self.inserts = []
        self.counter = 0

    def next(self):
        counter = self.counter
        self.counter += 1
        return counter

    def reset(self):
        self.counter = 0

    def insert_signals(self, dataset, signals, samples, times):
        self.inserts.append(dbm.Insert(dataset, signals, samples, times))
        
    def fetch_signals(self, result, dataset, signals, interval):
        self.reset()
        self.queries.append(dbm.Query(dataset, signals, interval))
        for x in range(3):
            result.add(list(map(lambda x: self.next(), signals)), interval.start + timedelta(seconds=self.counter))
                
    def aggregate_signals(self, result, dataset, signals, interval, aggregation):
        self.reset()
        self.queries.append(dbm.Query(dataset, signals, interval, aggregation))
        for signal in signals:
            result.set(signal, self.next())

class TestDatabaseManager(TestCase):
    def test_interval_eq(self):
        self.assertEqual(dbm.Interval(1, 2),
                         dbm.Interval(1, 2))
        
        self.assertNotEqual(dbm.Interval(1, 8),
                            dbm.Interval(1, 2))
        self.assertNotEqual(dbm.Interval(1, 2),
                            dbm.Interval(1, 9))
        self.assertNotEqual(dbm.Interval(1, 2),
                            dbm.Interval(2, 2))
    
    def test_query_eq(self):
        self.assertEqual(dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(datetime1, datetime2)),
                         dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(datetime1, datetime2)))
        self.assertNotEqual(dbm.Query('name', ['s1', 's5', 's3'], dbm.Interval(datetime1, datetime2)),
                            dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(datetime1, datetime2)))
        self.assertNotEqual(dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(datetime3, datetime2)),
                            dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(datetime1, datetime2)))
    
    def test_parse_query_jsons(self):
        self.assertEqual(dbm.parse_query_json(f'''
{{
    "queries": [
        {{
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {{
                "start": "{datetime_string1}",
                "end": "{datetime_string2}"
            }}
        }}
    ]
}}
        '''), [dbm.Query('somename', ['va', 'vb', 'vc'],
                         dbm.Interval(datetime1, datetime2))])

        self.assertEqual(dbm.parse_query_json(f'''
{{
    "queries": [
        {{
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {{
                "start": "{datetime_string1}",
                "end": "{datetime_string2}"
            }}
        }},
        {{
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {{
                "start": "{datetime_string2}",
                "end": "{datetime_string3}"
            }}
        }}
    ]
}}
        '''), [dbm.Query('somename', ['va', 'vb', 'vc'], dbm.Interval(datetime1, datetime2)),
               dbm.Query('otherthing', ['ia', 'ib'], dbm.Interval(datetime2, datetime3))])


        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries".'):
            dbm.parse_query_json(f'''
{{
    "queries": [
    ]
}}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[0\].dataset".'):
            dbm.parse_query_json(f'''
{{
    "queries": [
        {{
            "signals": ["ia", "ib"],
            "interval": {{
                "start": "{datetime_string1}",
                "end": "{datetime_string3}"
            }}
        }}
    ]
}}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[0\].interval.start".'):
            dbm.parse_query_json(f'''
{{
    "queries": [
        {{
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {{
                "end": "{datetime_string2}"
            }}
        }}
    ]
}}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[1\].interval.end".'):            
            dbm.parse_query_json(f'''
{{
    "queries": [
        {{
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {{
                "start": "{datetime_string1}",
                "end": "{datetime_string3}"
            }}
        }},
        {{
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {{
                "start": "{datetime_string2}"
            }}
        }}
    ]
}}
            ''')

    def test_parse_insert_jsons(self):
        self.assertEqual(dbm.parse_insert_json(f'''
{{
    "inserts": [
        {{
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "samples": [[1, 2, 3], [3, 4, 5]],
            "times": ["{datetime_string1}", "{datetime_string2}"]
        }}
    ]
}}
        '''), [dbm.Insert('somename', ['va', 'vb', 'vc'],
                          [[1,2,3], [3,4,5]],
                          [datetime1, datetime2])])

        self.assertEqual(dbm.parse_insert_json(f'''
{{
    "inserts": [
        {{
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "samples": [[1, 2, 3], [3, 4, 5]],
            "times": ["{datetime_string1}", "{datetime_string2}"]
        }},
        {{
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "samples": [[1, 2], [3, 4]],
            "times": ["{datetime_string2}", "{datetime_string3}"]
        }}
    ]
}}
        '''), [dbm.Insert('somename', ['va', 'vb', 'vc'], [[1, 2, 3], [3, 4, 5]], [datetime1, datetime2]),
               dbm.Insert('otherthing', ['ia', 'ib'], [[1, 2], [3, 4]], [datetime2, datetime3])])


        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "inserts".'):
            dbm.parse_insert_json(f'''
{{
    "inserts": [
    ]
}}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "inserts\[0\].dataset".'):
            dbm.parse_insert_json(f'''
{{
    "inserts": [
        {{
            "signals": ["ia", "ib"],
            "samples": [[1, 2], [3, 4]],
            "times": ["{datetime_string2}", "{datetime_string3}"]
        }}
    ]
}}
        ''')

    def test_data_store_execute_queries(self):
        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(datetime1, datetime2))]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(datetime1, datetime2)),
                   dbm.Query('name2', ['a2', 'b48', 'VIA'], dbm.Interval(datetime1, datetime3))]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(datetime1, datetime2), 'max'),
                   dbm.Query('name2', ['a2', 'b48', 'VIA'], dbm.Interval(datetime2, datetime3), 'min')]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)


    def test_data_store_execute_inserts(self):
        ds = MockDataStore()
        inserts = [dbm.Insert('name1', ['s1', 's2', 'sb'], [[1,2,3], [4,5,6]], [datetime1, datetime2])]
        ds.execute_inserts(inserts)
        self.assertEqual(inserts, ds.inserts)

        ds = MockDataStore()
        inserts = [dbm.Insert('name1', ['s1', 's2', 'sb'], [[1,2,3], [4,5,6]], [datetime1, datetime2]),
                   dbm.Insert('name2', ['ab', 'dc'], [[5,4], [3,2], [9,8], [32,54]], [datetime2, datetime3, datetime4, datetime5])]
        ds.execute_inserts(inserts)
        self.assertEqual(inserts, ds.inserts)

    def test_data_store_signal_query_results(self):
        query = dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(datetime2, datetime4))
        result = dbm.SignalQueryResult(query)
        result.add([1, 2, 3], datetime3)
        result.add([8, 9, 6], datetime4)
        self.assertEqual(result.to_dict(), {
            'samples': [[1, 2, 3], [8, 9, 6]],
            'times': [datetime3, datetime4],
            'query': {
                'dataset': 'name1',
                'signals': ['s1', 's2', 'sb'],
                'interval': {
                    'start': datetime2,
                    'end': datetime4,
                }
            }
        })

        # No results
        result = dbm.SignalQueryResult(query)
        self.assertEqual(result.to_dict(), {
            'samples': [],
            'times': [],
            'query': {
                'dataset': 'name1',
                'signals': ['s1', 's2', 'sb'],
                'interval': {
                    'start': datetime2,
                    'end': datetime4,
                }
            }
        })

        with self.assertRaisesRegex(Exception, 'Must provide a value for every signal value.'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13], datetime3) # missing a value for 'sb'

        with self.assertRaisesRegex(Exception, f'Given time "{datetime_string1}" is out-of-bounds of the query interval \(between "{datetime_string2}" and "{datetime_string4}"\).'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13, 32], datetime1) # time too early

        with self.assertRaisesRegex(Exception, f'Given time "{datetime_string5}" is out-of-bounds of the query interval \(between "{datetime_string2}" and "{datetime_string4}"\).'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13, 32], datetime5) # time too late

        result = dbm.SignalQueryResult(query)
        result.add([10, 13, 32], datetime5, validate=False) # time too late - but skipping validation

        with self.assertRaisesRegex(Exception, f'Received time value "{datetime_string2}" in non-monotonically increasing order.'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13, 14], datetime3)
            result.add([1, 2, 3], datetime4)
            result.add([94, 83, 12], datetime2)

    def test_data_store_aggregate_query_results(self):
        query = dbm.Query('sampleag', ['AGGG8', 'AG9'], dbm.Interval(datetime2, datetime4), 'max')
        result = dbm.AggregateQueryResult(query)
        result.set('AGGG8', 392)
        result.set('AG9', 899209)
        self.assertEqual(result.to_dict(), {
            'results': [392, 899209],
            'query': {
                'dataset': 'sampleag',
                'signals': ['AGGG8', 'AG9'],
                'interval': {
                    'start': datetime2,
                    'end': datetime4,
                },
                'aggregation': 'max',
            }
        })

        # No results
        result = dbm.AggregateQueryResult(query)
        self.assertEqual(result.to_dict(), {
            'results': [0, 0],
            'query': {
                'dataset': 'sampleag',
                'signals': ['AGGG8', 'AG9'],
                'interval': {
                    'start': datetime2,
                    'end': datetime4,
                },
                'aggregation': 'max',
            }
        })

        with self.assertRaisesRegex(Exception, 'Invalid signal name "badvalue".'):
            result.set('badvalue', 93)

    def test_data_store_query(self):
        query_json = {
            'queries': [
                {
                    'dataset': 'somename',
                    'signals': ['va', 'vb', 'vc'],
                    'interval': {
                        'start': datetime_string2,
                        'end': datetime_string4
                    },
                    'aggregation': 'max'
                },
                {
                    'dataset': 'otherthing',
                    'signals': ['ia', 'ib'],
                    'interval': {
                        'start': datetime_string3,
                        'end': datetime_string5
                    }
                }
            ],
        }

        # See MockDataStore implementation as to why the results are spaced out by seconds:
        self.assertEqual(MockDataStore.query(query_json), {
            'results': [
                {
                    'results': [0, 1, 2],
                    'query': {
                        'dataset': 'somename',
                        'signals': ['va', 'vb', 'vc'],
                        'interval': {
                            'start': datetime2,
                            'end': datetime4,
                        },
                        'aggregation': 'max'
                    },
                },
                {
                    'samples': [[0, 1], [2, 3], [4, 5]],
                    'times': [datetime3+timedelta(seconds=2), datetime3+timedelta(seconds=4), datetime3+timedelta(seconds=6)],
                    'query': {
                        'dataset': 'otherthing',
                        'signals': ['ia', 'ib'],
                        'interval': {
                            'start': datetime3,
                            'end': datetime5,
                        }
                    }
                }
            ]
        })

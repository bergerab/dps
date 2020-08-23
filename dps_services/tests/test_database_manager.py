from unittest import TestCase
from datetime import datetime, timedelta

import dps_services.database_manager as dbm
import dps_services.util as util

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
        self.assertEqual(dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(1, 2)),
                         dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(1, 2)))
        self.assertNotEqual(dbm.Query('name', ['s1', 's5', 's3'], dbm.Interval(1, 2)),
                            dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(1, 2)))
        self.assertNotEqual(dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(9, 2)),
                            dbm.Query('name', ['s1', 's2', 's3'], dbm.Interval(1, 2)))
    
    def test_parse_query_requests(self):
        self.assertEqual(dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "start": 29292929,
                "end": 3939393939
            }
        }
    ]
}
        '''), [dbm.Query('somename', ['va', 'vb', 'vc'], dbm.Interval(29292929, 3939393939))])

        self.assertEqual(dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "start": 39,
                "end": 8833
            }
        },
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "start": 9,
                "end": 19
            }
        }
    ]
}
        '''), [dbm.Query('somename', ['va', 'vb', 'vc'], dbm.Interval(39, 8833)),
               dbm.Query('otherthing', ['ia', 'ib'], dbm.Interval(9, 19))])


        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries".'):
            dbm.parse_query_request('''
{
    "queries": [
    ]
}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[0\].dataset".'):
            dbm.parse_query_request('''
{
    "queries": [
        {
            "signals": ["ia", "ib"],
            "interval": {
                "start": 9,
                "end": 19
            }
        }
    ]
}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[0\].interval.start".'):
            dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "end": 19
            }
        }
    ]
}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[1\].interval.end".'):            
            dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "start": 39,
                "end": 8833
            }
        },
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "start": 9
            }
        }
    ]
}
            ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[1\].interval.end".'):            
            dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "start": 39,
                "end": 8833
            }
        },
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "start": 9
            }
        }
    ]
}
            ''')            
            

    def test_data_store_execute_queries(self):
        class MockDataStore(dbm.DataStore):
            def __init__(self):
                self.queries = []
            
            def fetch_signals(self, result, dataset, signals, interval):                
                self.queries.append(dbm.Query(dataset, signals, interval))
                
            def aggregate_signals(self, result, dataset, signals, interval, aggregation):
                self.queries.append(dbm.Query(dataset, signals, interval, aggregation))                

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(3, 82))]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(3, 82)),
                   dbm.Query('name2', ['a2', 'b48', 'VIA'], dbm.Interval(2929, 4444))]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(3, 82), 'max'),
                   dbm.Query('name2', ['a2', 'b48', 'VIA'], dbm.Interval(2929, 4444), 'min')]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

    def test_data_store_signal_query_results(self):
        query = dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(3, 82))
        result = dbm.SignalQueryResult(query)
        result.add([1, 2, 3], 4)
        result.add([8, 9, 6], 5)
        self.assertEqual(result.to_dict(), {
            'samples': [[1, 2, 3], [8, 9, 6]],
            'times': [4, 5],
            'query': {
                'dataset': 'name1',
                'signals': ['s1', 's2', 'sb'],
                'interval': {
                    'start': 3,
                    'end': 82,
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
                    'start': 3,
                    'end': 82,
                }
            }
        })

        with self.assertRaisesRegex(Exception, 'Must provide a value for all signal values in each call.'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13], 1) # missing a value for 'sb'

        with self.assertRaisesRegex(Exception, 'Given time "1" is out-of-bounds of the query interval \(between "3" and "82"\).'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13, 32], 1) # time too early

        with self.assertRaisesRegex(Exception, 'Given time "90" is out-of-bounds of the query interval \(between "3" and "82"\).'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13, 32], 90) # time too late

        result = dbm.SignalQueryResult(query)
        result.add([10, 13, 32], 90, validate=False) # time too late - but skipping validation

        with self.assertRaisesRegex(Exception, 'Received time value "5" in non-monotonically increasing order.'):
            result = dbm.SignalQueryResult(query)
            result.add([10, 13, 14], 10)
            result.add([1, 2, 3], 20)
            result.add([94, 83, 12], 5)

    def test_data_store_aggregate_query_results(self):
        query = dbm.Query('sampleag', ['AGGG8', 'AG9'], dbm.Interval(90, 10000), 'max')
        result = dbm.AggregateQueryResult(query)
        result.set('AGGG8', 392)
        result.set('AG9', 899209)
        self.assertEqual(result.to_dict(), {
            'results': [392, 899209],
            'query': {
                'dataset': 'sampleag',
                'signals': ['AGGG8', 'AG9'],
                'interval': {
                    'start': 90,
                    'end': 10000,
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
                    'start': 90,
                    'end': 10000,
                },
                'aggregation': 'max',
            }
        })

        with self.assertRaisesRegex(Exception, 'Invalid signal name "badvalue".'):
            result.set('badvalue', 93)

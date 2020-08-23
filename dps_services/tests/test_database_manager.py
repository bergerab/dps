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
                "from": 29292929,
                "to": 3939393939
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
                "from": 39,
                "to": 8833
            }
        },
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "from": 9,
                "to": 19
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
                "from": 9,
                "to": 19
            }
        }
    ]
}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[0\].interval.from".'):
            dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "to": 19
            }
        }
    ]
}
        ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[1\].interval.to".'):            
            dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "from": 39,
                "to": 8833
            }
        },
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "from": 9
            }
        }
    ]
}
            ''')

        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "queries\[1\].interval.to".'):            
            dbm.parse_query_request('''
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "from": 39,
                "to": 8833
            }
        },
        {
            "dataset": "otherthing",
            "signals": ["ia", "ib"],
            "interval": {
                "from": 9
            }
        }
    ]
}
            ''')            
            

    def test_data_store(self):
        class MockDataStore(dbm.DataStore):
            def __init__(self):
                self.queries = []
            
            def query(self, dataset, signals, interval, aggregation=None):
                self.queries.append(dbm.Query(dataset, signals, interval, aggregation))

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(3, 82), 'meatball')]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

        ds = MockDataStore()
        queries = [dbm.Query('name1', ['s1', 's2', 'sb'], dbm.Interval(3, 82), 'meatball'),
                   dbm.Query('name2', ['a2', 'b48', 'VIA'], dbm.Interval(2929, 4444), 'am')]
        ds.execute_queries(queries)
        self.assertEqual(queries, ds.queries)

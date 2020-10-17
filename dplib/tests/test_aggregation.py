from unittest import TestCase
from datetime import datetime, timedelta

import dplib.aggregation as agg
from dplib import Series

def make_dict(name, rest):
    rest['name'] = name
    return rest

class TestAggregation(TestCase):
    def test_eq(self):
        self.assertEqual(agg.MinAggregation(None, 2),
                         agg.MinAggregation(None, 2))
        self.assertNotEqual(agg.MinAggregation(None, 8),
                            agg.MinAggregation(None, 2))
        self.assertEqual(agg.AddAggregation(None, 8, 2),
                         agg.AddAggregation(None, 8, 2))
        self.assertNotEqual(agg.AddAggregation(None, 80, 32),
                         agg.AddAggregation(None, 80, 2))
    
    def test_overrides(self):
        self.assertEqual((1 + agg.Aggregation(None, 3)).get_value(), 1 + 3)
        self.assertEqual((agg.Aggregation(None, 7) + 3).get_value(), 7 + 3)
        self.assertEqual((3 - agg.Aggregation(None, 7)).get_value(), 3 - 7)                        
        self.assertEqual((agg.Aggregation(None, 7) - 3).get_value(), 7 - 3)
        self.assertEqual((3 * agg.Aggregation(None, 7)).get_value(), 3 * 7)                        
        self.assertEqual((agg.Aggregation(None, 7) * 3).get_value(), 7 * 3)
        self.assertEqual((3 / agg.Aggregation(None, 7)).get_value(), 3 / 7)                        
        self.assertEqual((agg.Aggregation(None, 7) / 3).get_value(), 7 / 3)                
        self.assertEqual((3 // agg.Aggregation(None, 7)).get_value(), 3 // 7)                        
        self.assertEqual((agg.Aggregation(None, 7) // 3).get_value(), 7 // 3)                
    
    def test_merge(self):
        self.assertEqual(agg.MinAggregation(None, 38)
                        .merge(agg.MinAggregation(None, 34))
                        .merge(agg.MinAggregation(None, 129))
                        .merge(agg.MinAggregation(None, 37)).get_value(), 34)

        self.assertEqual(agg.MaxAggregation(None, 38)
                        .merge(agg.MaxAggregation(None, 34))
                        .merge(agg.MaxAggregation(None, 129))
                        .merge(agg.MaxAggregation(None, 99)).get_value(), 129)

        v1 = [1, 2, 3, 4]
        v2 = [3, 19, 2]
        v3 = [1.2, 3]
        v4 = [5.3, 23, 4, 2]
        self.assertEqual(agg.AverageAggregation.from_series(Series(v1))
                        .merge(agg.AverageAggregation.from_series(Series(v2)))
                        .merge(agg.AverageAggregation.from_series(Series(v3)))
                        .merge(agg.AverageAggregation.from_series(Series(v4))).get_value(),
                         sum(v1 + v2 + v3 + v4) / len(v1 + v2 + v3 + v4))

        self.assertEqual(agg.AddAggregation(None, 1, 2)
                        .merge(agg.AddAggregation(None, 3, 4))
                        .merge(agg.AddAggregation(None, 9, 3))
                        .merge(agg.AddAggregation(None, 99, 2)).get_value(), 99 + 2)

    def test_get_value(self):
        self.assertEqual(agg.AverageAggregation.from_series(Series([1,2,3,4,5])).get_value(),
                         sum([1,2,3,4,5]) / len([1,2,3,4,5]))
        self.assertEqual(agg.MinAggregation(None, 38).get_value(), 38)
        self.assertEqual(agg.MaxAggregation(None, 11).get_value(), 11)
        self.assertEqual(agg.AddAggregation(None, 93, 28).get_value(), 93 + 28)
        self.assertEqual(agg.SubAggregation(None, 23, 77).get_value(), 23 - 77)
        self.assertEqual(agg.MulAggregation(None, 3, 8).get_value(), 3 * 8)
        self.assertEqual(agg.DivAggregation(None, 39, 192).get_value(), 39 / 192)
        self.assertEqual(agg.FloorDivAggregation(None, 293, 123).get_value(), 293 // 123)
        
        self.assertEqual(agg.AddAggregation(None, 293, agg.AddAggregation(None, 39, 22)).get_value(), 293 + 39 + 22)
        self.assertEqual(agg.SubAggregation(None, agg.MulAggregation(None, 8, 23), agg.DivAggregation(None, 39, 22)).get_value(),
                         8 * 23 - 39 / 22)
        self.assertEqual(agg.MulAggregation(None, 0.04, agg.MaxAggregation(None, 96)).get_value(), 0.04 * 96)
        
    def test_to_dict(self):
        self.assertEqual(agg.AverageAggregation.from_sum_and_count(None, 20, 3).to_dict(), make_dict('average', {
            'average': 20 / 3,
            'count': 3,
        }))

        self.assertEqual(agg.MinAggregation(None, 93).to_dict(), make_dict('min', {
            'value': 93,
        }))

        self.assertEqual(agg.MaxAggregation(None, 302).to_dict(), make_dict('max', {
            'value': 302,
        }))

        self.assertEqual(agg.MaxAggregation(None, 302).to_dict(), make_dict('max', {
            'value': 302,
        }))

        self.assertEqual(agg.AddAggregation(None, 6, 7).to_dict(), make_dict('add', {
            'lhs': {
                'name': 'constant',
                'value': 6,
            },
            'rhs': {
                'name': 'constant',
                'value': 7,
            },            
        }))

        self.assertEqual(agg.SubAggregation(None, 4, 1).to_dict(), make_dict('sub', {
            'lhs': {
                'name': 'constant',
                'value': 4,
            },
            'rhs': {
                'name': 'constant',
                'value': 1,
            },            
        }))
        
        self.assertEqual(agg.MulAggregation(None, -3, 99).to_dict(), make_dict('mul', {
            'lhs': {
                'name': 'constant',
                'value': -3,
            },
            'rhs': {
                'name': 'constant',
                'value': 99,
            },            
        }))

        self.assertEqual(agg.DivAggregation(None, 12, 24).to_dict(), make_dict('div', {
            'lhs': {
                'name': 'constant',
                'value': 12,
            },
            'rhs': {
                'name': 'constant',
                'value': 24,
            },            
        }))

    def test_from_dict(self):
        self.assertEqual(agg.Aggregation.from_dict({
            'name': 'constant',
            'value': 30,
        }).to_dict(), agg.Aggregation(None, 30).to_dict())

        self.assertEqual(agg.Aggregation.from_dict({
            'name': 'max',
            'value': 29,
        }).to_dict(), agg.MaxAggregation(None, 29).to_dict())

        self.assertEqual(agg.Aggregation.from_dict({
            'name': 'min',
            'value': 12,
        }).to_dict(), agg.MinAggregation(None, 12).to_dict())

        self.assertEqual(agg.Aggregation.from_dict({
            'name': 'average',
            'average': 392,
            'count': 2,
        }).to_dict(), agg.AverageAggregation(None, 392, 2).to_dict())

        self.assertEqual(agg.Aggregation.from_dict({
            'name': 'add',
            'lhs': {
                'name': 'constant',
                'value': 12,
            },
            'rhs': {
                'name': 'constant',
                'value': 94,
            },
        }).to_dict(), agg.AddAggregation(None, 12, 94).to_dict())
        
test_suite = TestAggregation

from unittest import TestCase
from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal

import pandas as pd

from dplib.component import Component
from dplib.result import Result
from dplib.testing import ResultAssertions
from dplib.aggregation import AverageAggregation, AddAggregation, MulAggregation
from dplib import Series, Dataset

from dplib.aggregation import Aggregation

NOW = datetime.now()

TIME1 = [
    NOW,
    NOW + timedelta(seconds=1),
    NOW + timedelta(seconds=2)
]
D1 = Dataset({
    'A': Series([7, 6, 5], TIME1),
    'B': Series([9, 8, 7], TIME1),
})

TIME1_LONG = list(map(lambda x: timedelta(seconds=x) + NOW, range(10)))
D1_LONG = Dataset({
    'A': Series(range(10), TIME1_LONG),
    'B': Series(range(10, 20), TIME1_LONG),
})
D1_LONG_COUT = Dataset({
    'A': Series(range(10), TIME1_LONG, cout_enabled=True),
    'B': Series(range(10, 20), TIME1_LONG, cout_enabled=True),
})

D1_MAPPED = Dataset({
    'E': Series([7, 6, 5], TIME1),
    'D': Series([9, 8, 7], TIME1),
})

TIME1_PART_2 = [
    NOW + timedelta(seconds=3),
    NOW + timedelta(seconds=4),
    NOW + timedelta(seconds=5)
]
D1_PART_2 = Dataset({
    'A': Series([11, 23, 9], TIME1_PART_2),
    'B': Series([27, 38, 4], TIME1_PART_2),
})

D1_BASIC_RESULT = Dataset({
    'KPI One': Series([7 + 9, 6 + 8, 5 + 7], TIME1),
})

D1_AVG_RESULT = {
    'KPI One': sum([7 + 9, 6 + 8, 5 + 7]) / 3
}

D1_AVG_DEP_RESULT = {
    'PlusAvgSum': (sum([7 + 9, 6 + 8, 5 + 7]) / 3) + 2,    
}

D1_DEPENDENT_RESULT = Dataset({
    'KPI Two': Series([7 + 9 + 9, 6 + 8 + 8, 5 + 7 + 7], TIME1),
})

D1_DEPENDENT_RESULT_BOTH = Dataset({
    'KPI One': Series([7 + 9, 6 + 8, 5 + 7], TIME1),    
    'KPI Two': Series([7 + 9 + 9, 6 + 8 + 8, 5 + 7 + 7], TIME1),
})

TIME2 = [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]
D2 = Dataset({
    'A': Series([1, 2, 3], TIME2),
    'B': Series([4, 5, 6], TIME2),
    'C': Series([7, 8, 9], TIME2),
    'D': Series([10, 11, 12], TIME2),        
})

D2_RESULT = Dataset({
    'KPI One': Series([1 + 4, 2 + 5, 3 + 6], TIME2),
    'KPI Two': Series([7 + 2, 8 + 2, 9 + 2], TIME2),
    'KPI Three': Series([4 + 10, 5 + 11, 6 + 12], TIME2),
})

D3_MISSING_PART1_TIME = [
    NOW + timedelta(seconds=0),
    NOW + timedelta(seconds=1),
    NOW + timedelta(seconds=2)
]
D3_MISSING_PART1 = Dataset({
    'A': Series([1, 2, 3], D3_MISSING_PART1_TIME),
    'B': Series([10, 11, 12], D3_MISSING_PART1_TIME),
})

D3_MISSING_PART2_TIME = [
    NOW + timedelta(seconds=3),
    NOW + timedelta(seconds=4),
    NOW + timedelta(seconds=5)
]
D3_MISSING_PART2 = Dataset({
    'A': Series([None, None, None], D3_MISSING_PART2_TIME),
    'B': Series([13, 14, 15], D3_MISSING_PART2_TIME),
})

D3_MISSING_PART3_TIME = [
    NOW + timedelta(seconds=6),
    NOW + timedelta(seconds=7),
    NOW + timedelta(seconds=8)
]
D3_MISSING_PART3 = Dataset({
    'A': Series([None, None, None], D3_MISSING_PART3_TIME),
    'B': Series([16, 17, 18], D3_MISSING_PART3_TIME),
})

class TestComponent(TestCase, ResultAssertions):
    def test_get_required_inputs(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B', id='K1') \
            .add('KPI Two', 'C + D', id='K2') \
            .add('KPI Three', 'K1 + K2')
        self.assertEqual(SUT.get_required_inputs(['KPI Three']), {
            'A', 'B', 'C', 'D'
        })
    
    def test_aggregation_continue_advanced_merge_weighted_eff(self):
        SUT = Component('System Under Test') \
            .add('WeightedEfficiencyTest', 'max(A) * 0.02 + avg(B) * 0.25')
        result = SUT.run(D1, 'WeightedEfficiencyTest')
        result = SUT.run(D1_PART_2, 'WeightedEfficiencyTest', previous_result=result)
        self.assertResultEqual(result.get_aggregations(), {
            'WeightedEfficiencyTest': max([7, 6, 5, 11, 23, 9]) * 0.02 + (sum([9, 8, 7, 27, 38, 4])/6) * 0.25,
        })
    
    def test_aggregation_continue_advanced_merge(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)') \
            .add('PlusAvgSum', 'AvgSum + 2')            
        result = SUT.run(D1, ['Sum', 'PlusAvgSum'])
        result = SUT.run(D1_PART_2, ['Sum', 'PlusAvgSum'], previous_result=result)

        expected_result = Result(Dataset({
            'Sum': Series([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4],
                          [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                           NOW + timedelta(seconds=3), NOW + timedelta(seconds=4),
                           NOW + timedelta(seconds=5)]),
        }), aggregations_for_ui={
            'PlusAvgSum': AddAggregation(None, AverageAggregation(None, sum([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4]) / 6, 6), 2),    
        })
        self.assertResultEqual(expected_result, result)
    
    def test_aggregation_continue(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)')
        result = SUT.run(D1, ['AvgSum', 'Sum'])
        result = SUT.run(D1_PART_2, ['AvgSum', 'Sum'], previous_result=result)

        expected_result = Result(Dataset({
            'Sum': Series([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4],
                          [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                           NOW + timedelta(seconds=3), NOW + timedelta(seconds=4), NOW + timedelta(seconds=5)]),
        }), aggregations_for_ui={
            'AvgSum': AverageAggregation(None, sum([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4]) / 6, 6),    
        })
        self.assertResultEqual(expected_result, result)

    def test_aggregation_continue_advanced(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', '1 + avg(Sum)')
        result = SUT.run(D1, ['AvgSum', 'Sum'])
        result = SUT.run(D1_PART_2, ['AvgSum', 'Sum'], previous_result=result)

        expected_result = Result(Dataset({
            'Sum': Series([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4],
                          [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                           NOW + timedelta(seconds=3), NOW + timedelta(seconds=4), NOW + timedelta(seconds=5)]),
        }), aggregations_for_ui={
            'AvgSum': AddAggregation(None, Aggregation(None, 1), AverageAggregation(None, sum([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4]) / 6, 6)),    
        })
        self.assertResultEqual(expected_result, result)

    def test_aggregation_continue_advanced_with_missing_data(self):
        SUT = Component('System Under Test') \
            .add('AvgA', 'avg(B) + avg(A)') \
            .add('Dink', 'AvgA')
        result = SUT.run(D3_MISSING_PART1, ['Dink'])
        result = SUT.run(D3_MISSING_PART2, ['Dink'], previous_result=result)
        result = SUT.run(D3_MISSING_PART3, ['Dink'], previous_result=result)

        expected_result = Result(aggregations_for_ui={
            'Dink': AddAggregation(None, AverageAggregation(None, sum([10, 11, 12, 13, 14, 15, 16, 17, 18]) / 9, 9), AverageAggregation(None, sum([1, 2, 3]) / 3, 3)),    
        })
        self.assertResultEqual(expected_result, result)

    def test_df_and_aggregation_result(self):
        # Component.run can return both a Dataset of KPIs (time-series data),
        # and aggregations of data.
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)') \
            .add('PlusAvgSum', 'AvgSum + 2')
        result = SUT.run(D1, ['PlusAvgSum', 'Sum'])
        self.assertResultEqual(Result(Dataset({
            'Sum': Series([7 + 9, 6 + 8, 5 + 7],
                          [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]),
        }), aggregations_for_ui={
            'PlusAvgSum': AddAggregation(None, AverageAggregation(None, sum([7 + 9, 6 + 8, 5 + 7]) / 3, 3), 2),    
        }), result)

    def test_mapping(self):
        SUT = Component('System Under Test') \
            .add('Sum', '(A * P1) + (B * P2)')
        P1 = 3.1
        P2 = 7.3
        result = SUT.run(D1, 'Sum', {
            'P1': P1,
            'P2': P2,
        })
        self.assertResultEqual(Dataset({
            'Sum': Series([(7 * P1) + (9 * P2), (6 * P1) + (8 * P2), (5 * P1) + (7 * P2)],
                          [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]),
        }), result.dataset)

        SUT = Component('System Under Test') \
            .add('Sum', '(A * P1) + (B * P2)')
        result = SUT.run(D1_MAPPED, 'Sum', {
            'A': 'E',
            'B': 'D',
            'P1': P1,
            'P2': P2,
        })
        self.assertResultEqual(Dataset({
            'Sum': Series([(7 * P1) + (9 * P2), (6 * P1) + (8 * P2), (5 * P1) + (7 * P2)],
                          [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]),
        }), result.dataset)
    
    def test_aggregation_with_dependent(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)') \
            .add('PlusAvgSum', 'AvgSum + 2')
        result = SUT.run(D1, 'PlusAvgSum')
        self.assertResultEqual(D1_AVG_DEP_RESULT, result.get_aggregations_for_ui())

    def test_aggregation_persists_values(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'avg(A + B)')
        
        RESULT = Dataset({
            'KPI One': Series([7+9, 6+8, 5+7],
                              [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]),
        })
        
        self.assertEqual(RESULT, SUT.run(D1, 'KPI One').get_intermidiate_values())
    
    def test_aggregation(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'avg(A + B)')
        self.assertResultEqual(D1_AVG_RESULT, SUT.run(D1, 'KPI One').get_aggregations())

    def test_window_with_cout(self):
        SUT = Component('System Under Test') \
            .add('2s Avg', 'avg(window(A, "2s"))')
        result = SUT.run(D1_LONG_COUT, '2s Avg')
        expected_result = Dataset({
            '2s Avg': Series([
                (0 + 1) / 2,
                (2 + 3) / 2,
                (4 + 5) / 2,
                (6 + 7) / 2,
            ], [
                TIME1_LONG[0],
                TIME1_LONG[2],
                TIME1_LONG[4],
                TIME1_LONG[6],
            ], cout=pd.Series([8, 9], index=[TIME1_LONG[8],
                                             TIME1_LONG[9]])),
        })        
        self.assertResultEqual(expected_result, result)

    def test_window(self):
        SUT = Component('System Under Test') \
            .add('2s Avg', 'avg(window(A, "2s"))')
        result = SUT.run(D1_LONG, '2s Avg')
        expected_result = Dataset({
            '2s Avg': Series([
                (0 + 1) / 2,
                (2 + 3) / 2,
                (4 + 5) / 2,
                (6 + 7) / 2,
                (8 + 9) / 2,                
            ], [
                TIME1_LONG[0],
                TIME1_LONG[2],
                TIME1_LONG[4],
                TIME1_LONG[6],
                TIME1_LONG[8],                
            ])
        })
        self.assertResultEqual(expected_result, result)

    def test_basic(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B')
        self.assertResultEqual(D1_BASIC_RESULT, SUT.run(D1, 'KPI One'))

    def test_passing_window(self):
        SUT = Component('System Under Test', parameters=['WindowSize']) \
            .add('KPI One', 'avg(window(A + B, WindowSize))')
        self.assertResultEqual(D1_BASIC_RESULT, SUT.run(D1, 'KPI One', { 'WindowSize': timedelta(seconds=1) }))

    def test_multiple_basic(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B') \
            .add('KPI Two', 'C + 2') \
            .add('KPI Three', 'D + B')
        self.assertResultEqual(D2_RESULT, SUT.run(D2, ['KPI One', 'KPI Two', 'KPI Three']))

    def test_dependent(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B', id='KPI1') \
            .add('KPI Two', 'KPI1 + B')

        # Should automatically compute KPI One (but not show it in the output):
        self.assertResultEqual(D1_DEPENDENT_RESULT, SUT.run(D1, ['KPI Two']))
        
        self.assertResultEqual(D1_DEPENDENT_RESULT_BOTH, SUT.run(D1, ['KPI One', 'KPI Two']).dataset)

    def test_result_to_df(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B') \
            .add('KPI Two', 'C + 2') \
            .add('KPI Three', 'D + B')
        assert_frame_equal(pd.DataFrame(data={
            'KPI One': [1+4, 2+5, 3+6],
            'KPI Two': [7+2, 8+2, 9+2],
            'KPI Three': [10+4, 11+5, 12+6],
        }, index=TIME2), SUT.run(D2, ['KPI One', 'KPI Two', 'KPI Three']).get_dataframe())

test_suite = TestComponent

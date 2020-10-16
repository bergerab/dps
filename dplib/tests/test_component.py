from unittest import TestCase
from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal

import pandas as pd

from dplib.component import Component
from dplib.result import ResultAssertions, Result
from dplib.aggregation import AverageAggregation, AddAggregation

NOW = datetime.now()

DF1 = pd.DataFrame(data={
    'A': [7, 6, 5],
    'B': [9, 8, 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF1_MAPPED = pd.DataFrame(data={
    'E': [7, 6, 5],
    'D': [9, 8, 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF1_PART_2 = pd.DataFrame(data={
    'A': [11, 23, 9],
    'B': [27, 38, 4],
    'Time': [NOW + timedelta(seconds=3), NOW + timedelta(seconds=4), NOW + timedelta(seconds=5)],
})

DF2 = pd.DataFrame(data={
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9],
    'D': [10, 11, 12],        
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF1_BASIC_RESULT = pd.DataFrame(data={
    'KPI One': [7 + 9, 6 + 8, 5 + 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF1_AVG_RESULT = {
    'KPI One': sum([7 + 9, 6 + 8, 5 + 7]) / 3
}

DF1_AVG_DEP_RESULT = {
    'PlusAvgSum': (sum([7 + 9, 6 + 8, 5 + 7]) / 3) + 2,    
}

DF1_DEPENDENT_RESULT = pd.DataFrame(data={
    'KPI Two': [7 + 9 + 9, 6 + 8 + 8, 5 + 7 + 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF1_DEPENDENT_RESULT_BOTH = pd.DataFrame(data={
    'KPI One': [7 + 9, 6 + 8, 5 + 7],    
    'KPI Two': [7 + 9 + 9, 6 + 8 + 8, 5 + 7 + 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF2_RESULT = pd.DataFrame(data={
    'KPI One': [1 + 4, 2 + 5, 3 + 6],
    'KPI Two': [7 + 2, 8 + 2, 9 + 2],
    'KPI Three': [4 + 10, 5 + 11, 6 + 12],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
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
        result = SUT.run(DF1, 'WeightedEfficiencyTest')
        result = SUT.run(DF1_PART_2, 'WeightedEfficiencyTest', previous_result=result)
        self.assertResultEqual(result.get_aggregations(), {
            'WeightedEfficiencyTest': max([7, 6, 5, 11, 23, 9]) * 0.02 + (sum([9, 8, 7, 27, 38, 4])/6) * 0.25,
        })
    
    def test_aggregation_continue_advanced_merge(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)') \
            .add('PlusAvgSum', 'AvgSum + 2')            
        result = SUT.run(DF1, ['Sum', 'PlusAvgSum'])
        result = SUT.run(DF1_PART_2, ['Sum', 'PlusAvgSum'], previous_result=result)

        expected_result = Result(pd.DataFrame(data={
            'Sum': [7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4],
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                     NOW + timedelta(seconds=3), NOW + timedelta(seconds=4), NOW + timedelta(seconds=5)],
        }), {
            'PlusAvgSum': AddAggregation(AverageAggregation(sum([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4]) / 6, 6), 2),    
        })
        self.assertResultEqual(expected_result, result)
    
    def test_aggregation_continue(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)')
        result = SUT.run(DF1, ['AvgSum', 'Sum'])
        result = SUT.run(DF1_PART_2, ['AvgSum', 'Sum'], previous_result=result)

        expected_result = Result(pd.DataFrame(data={
            'Sum': [7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4],
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                     NOW + timedelta(seconds=3), NOW + timedelta(seconds=4), NOW + timedelta(seconds=5)],
        }), {
            'AvgSum': AverageAggregation(sum([7 + 9, 6 + 8, 5 + 7, 11 + 27, 23 + 38, 9 + 4]) / 6, 6),    
        })
        self.assertResultEqual(expected_result, result)

    def test_df_and_aggregation_result(self):
        # Component.run can return both a DataFrame of KPIs (time-series data),
        # and aggregations of data.
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)') \
            .add('PlusAvgSum', 'AvgSum + 2')
        result = SUT.run(DF1, ['PlusAvgSum', 'Sum'])
        self.assertResultEqual(Result(pd.DataFrame(data={
            'Sum': [7 + 9, 6 + 8, 5 + 7],
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
        }), {
            'PlusAvgSum': AddAggregation(AverageAggregation(sum([7 + 9, 6 + 8, 5 + 7]) / 3, 3), 2),    
        }), result)

    def test_mapping(self):
        SUT = Component('System Under Test') \
            .add('Sum', '(A * P1) + (B * P2)')
        P1 = 3.1
        P2 = 7.3
        result = SUT.run(DF1, 'Sum', {
            'P1': P1,
            'P2': P2,
        })
        self.assertResultEqual(pd.DataFrame(data={
            'Sum': [(7 * P1) + (9 * P2), (6 * P1) + (8 * P2), (5 * P1) + (7 * P2)],
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
        }), result.df)

        SUT = Component('System Under Test') \
            .add('Sum', '(A * P1) + (B * P2)')
        result = SUT.run(DF1_MAPPED, 'Sum', {
            'A': 'E',
            'B': 'D',
            'P1': P1,
            'P2': P2,
        })
        self.assertResultEqual(pd.DataFrame(data={
            'Sum': [(7 * P1) + (9 * P2), (6 * P1) + (8 * P2), (5 * P1) + (7 * P2)],
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
        }), result.df)
    
    def test_aggregation_with_dependent(self):
        SUT = Component('System Under Test') \
            .add('Sum', 'A + B') \
            .add('AvgSum', 'avg(Sum)') \
            .add('PlusAvgSum', 'AvgSum + 2')
        result = SUT.run(DF1, 'PlusAvgSum')
        self.assertResultEqual(DF1_AVG_DEP_RESULT, result.get_aggregations())
    
    def test_aggregation(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'avg(A + B)')
        self.assertResultEqual(DF1_AVG_RESULT, SUT.run(DF1, 'KPI One').get_aggregations())

    def test_basic(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B')
        self.assertResultEqual(DF1_BASIC_RESULT, SUT.run(DF1, 'KPI One'))

    def test_multiple_basic(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B') \
            .add('KPI Two', 'C + 2') \
            .add('KPI Three', 'D + B')
        self.assertResultEqual(DF2_RESULT, SUT.run(DF2, ['KPI One', 'KPI Two', 'KPI Three']))

    def test_dependent(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B', id='KPI1') \
            .add('KPI Two', 'KPI1 + B')

        # Should automatically compute KPI One (but not show it in the output):
        self.assertResultEqual(DF1_DEPENDENT_RESULT, SUT.run(DF1, ['KPI Two']))
        
        self.assertResultEqual(DF1_DEPENDENT_RESULT_BOTH, SUT.run(DF1, ['KPI One', 'KPI Two']).df)

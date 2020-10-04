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
    def test_df_and_aggregation_result(self):
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

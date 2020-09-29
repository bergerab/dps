from unittest import TestCase
from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal

import pandas as pd

from dplib.component import Component

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

DF1_DEPENDENT_RESULT = pd.DataFrame(data={
    'KPI Two': [7 + 9 + 9, 6 + 8 + 8, 5 + 7 + 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF2_RESULT = pd.DataFrame(data={
    'KPI One': [1 + 4, 2 + 5, 3 + 6],
    'KPI Two': [7 + 2, 8 + 2, 9 + 2],
    'KPI Three': [4 + 10, 5 + 11, 6 + 12],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

class TestComponent(TestCase):
    def test_basic(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B')
        assert_frame_equal(DF1_BASIC_RESULT, SUT.run(DF1, 'KPI One'))

    def test_multiple_basic(self):
        SUT = Component('System Under Test') \
            .add('KPI One', 'A + B') \
            .add('KPI Two', 'C + 2') \
            .add('KPI Three', 'D + B')
        assert_frame_equal(DF2_RESULT, SUT.run(DF2, ['KPI One', 'KPI Two', 'KPI Three']), check_like=True)

    def test_dependent(self):
        SUT = Component('System Under Test') \
            .add('KPI1', 'A + B') \
            .add('KPI Two', 'KPI1 + B')

        # Should automatically compute KPI One (but not show it in the output):
        assert_frame_equal(DF1_DEPENDENT_RESULT, SUT.run(DF1, 'KPI Two'))

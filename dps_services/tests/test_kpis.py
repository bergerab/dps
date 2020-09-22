from unittest import TestCase
from datetime import datetime, timedelta

import pandas as pd

from dplib import POWER

NOW = datetime.now()

DF1 = pd.DataFrame(data={
    'Voltage': [1.23, 5.32, 8.19],
    'Current': [0.32, -3.2, 4.2555],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

class TestKPIs(TestCase):
    def test_power(self):
        '''Tests a power KPI'''
        POWER.run('Power', DF1)

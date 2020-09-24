from unittest import TestCase
from datetime import datetime, timedelta

import pandas as pd

from dplib import KPI

NOW = datetime.now()

DF1 = pd.DataFrame(data={
    'Voltage': [1.23, 5.32, 8.19],
    'Current': [0.32, -3.2, 4.2555],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})

DF2 = pd.DataFrame(data={
    'volts': [1.23, 5.32, 8.19],
    'amps':  [0.32, -3.2, 4.2555],
    'my_time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})
'''
Same as DF1, but with different names.
'''

ID_KPI = KPI('x')
'''
An identity KPI. A KPI which simply returns the input value.
'''

POWER_KPI = KPI('Voltage * Current')
'''
Does a power computation (voltage times current).
'''

DF_POWER = pd.DataFrame(data={
    'Power': [1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})
'''
The result of multiplying Voltage and Current from DF1 and DF2.
'''

DF_POWER_WITHOUT_TIME = pd.DataFrame(data={
    'Power': [1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555],
})

class TestKPI(TestCase):
    def test_identity_kpi(self):
        '''Test a KPI that does a NOOP.'''
        df = ID_KPI.run('Identity', DF1, {
            'x': 'Voltage',
        })
        self.assertTrue(df.equals(DF1[['Voltage', 'Time']].rename(columns={ 'Voltage': 'Identity' })))

    def test_default_mappings(self):
        '''The default mappings should match the symbols used in the KPI computation.'''
        df = POWER_KPI.run('Power', DF1)
        self.assertTrue(df.equals(DF_POWER))

    def test_excluding_time_column(self):
        df = POWER_KPI.run('Power', DF1, include_time=False)
        self.assertTrue(df.equals(DF_POWER_WITHOUT_TIME))

    def test_mappings(self):
        '''The input DataFrame should be able to map its input column names (including the time column name).'''
        df = POWER_KPI.run('Power', DF2, {
            'Voltage': 'volts',
            'Current': 'amps',
        }, time_column='my_time').rename(columns={ 'my_time': 'Time' })
        self.assertTrue(df.equals(DF_POWER))

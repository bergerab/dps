from unittest import TestCase
from datetime import datetime, timedelta

import pandas as pd

from dplib import KPI
import dplib as dp
from dplib.result import Result

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

AVG_POWER_KPI = KPI('avg(Voltage * Current)')
MAX_POWER_KPI = KPI('max(Voltage * Current)')
MIN_POWER_KPI = KPI('min(Voltage * Current)')

COMPOUND_KPI = KPI('min(Voltage) * 0.2 + max(Current) * 0.6')

DF_POWER = Result(pd.DataFrame(data={
    'Power': [1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
}))
'''
The result of multiplying Voltage and Current from DF1 and DF2.
'''

AVG_DF_POWER = Result(pd.DataFrame(data={
    'Average Power': [sum([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555]) / 3],
}))

MAX_DF_POWER = Result(pd.DataFrame(data={
    'Max Power': [max([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555])],
}))

MIN_DF_POWER = Result(pd.DataFrame(data={
    'Min Power': [max([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555])],
}))

DF_POWER_WITHOUT_TIME = Result(pd.DataFrame(data={
    'Power': [1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555],
}))

DF_COMPOUND_KPI = Result(pd.DataFrame(data={
    'Value': [min([1.23, 5.32, 8.19]) * 0.2 + max([0.32, -3.2, 4.2555]) * 0.6],
}))

class TestKPI(TestCase):
    def test_identity_kpi(self):
        '''Test a KPI that does a NOOP.'''
        d = ID_KPI.run('Identity', DF1, {
            'x': 'Voltage',
        })
        self.assertTrue(d.equals(Result(DF1[['Voltage', 'Time']].rename(columns={ 'Voltage': 'Identity' }))))

    def test_default_mappings(self):
        '''The default mappings should match the symbols used in the KPI computation.'''
        d = POWER_KPI.run('Power', DF1)
        self.assertTrue(d.equals(DF_POWER))

    def test_compound_kpi(self):
        d = COMPOUND_KPI.run('Value', DF1)
        self.assertTrue(d.equals(DF_COMPOUND_KPI))

    def test_average_power(self):
        d = AVG_POWER_KPI.run('Average Power', DF1)
        self.assertTrue(d.equals(AVG_DF_POWER))

    def test_max_power(self):
        d = MAX_POWER_KPI.run('Max Power', DF1)
        self.assertTrue(d.equals(MAX_DF_POWER))        

    def test_min_power(self):
        d = MAX_POWER_KPI.run('Min Power', DF1)
        self.assertTrue(d.equals(MIN_DF_POWER))                

    def test_excluding_time_column(self):
        d = POWER_KPI.run('Power', DF1, include_time=False)
        self.assertTrue(d.equals(DF_POWER_WITHOUT_TIME))                        

    def test_mappings(self):
        '''The input DataFrame should be able to map its input column names (including the time column name).'''
        df = POWER_KPI.run('Power', DF2, {
            'Voltage': 'volts',
            'Current': 'amps',
        }, time_column='my_time').df.rename(columns={ 'my_time': 'Time' })
        self.assertTrue(df.equals(DF_POWER))

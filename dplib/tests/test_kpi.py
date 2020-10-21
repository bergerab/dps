from unittest import TestCase
from datetime import datetime, timedelta

from dplib import KPI
import dplib as dp
from dplib.result import Result
from dplib.result import ResultAssertions

NOW = datetime.now()

TIMES = [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]
D1 = dp.Dataset({
    'Voltage': dp.Series([1.23, 5.32, 8.19], TIMES),
    'Current': dp.Series([0.32, -3.2, 4.2555], TIMES),
})

D2 = dp.Dataset({
    'volts': dp.Series([1.23, 5.32, 8.19], TIMES),
    'amps':  dp.Series([0.32, -3.2, 4.2555], TIMES),
})
'''
Same as D1, but with different names.
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

D_POWER = dp.Dataset({
    'Power': dp.Series([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555], TIMES),
})
'''
The result of multiplying Voltage and Current from D1 and D2.
'''

class TestKPI(TestCase, ResultAssertions):
    def test_identity_kpi(self):
        '''Test a KPI that does a NOOP.'''
        result = ID_KPI.run('Identity', D1, {
            'x': 'Voltage',
        })
        self.assertResultEqual(result, Result(D1.select(['Voltage']).rename({ 'Voltage': 'Identity' })))

    def test_default_mappings(self):
        '''The default mappings should match the symbols used in the KPI computation.'''
        result = POWER_KPI.run('Power', D1)
        self.assertResultEqual(result, D_POWER)

    def test_compound_kpi(self):
        result = COMPOUND_KPI.run('Value', D1)
        self.assertEqual(result.get_aggregations(), {
            'Value': min([1.23, 5.32, 8.19]) * 0.2 + max([0.32, -3.2, 4.2555]) * 0.6,
        })

    def test_average_power(self):
        result = AVG_POWER_KPI.run('Average Power', D1)
        self.assertEqual(result.get_aggregations(), {
            'Average Power': sum([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555]) / 3,
        })

    def test_max_power(self):
        result = MAX_POWER_KPI.run('Max Power', D1)
        self.assertEqual(result.get_aggregations(), {
            'Max Power': max([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555]),
        })  

    def test_min_power(self):
        result = MAX_POWER_KPI.run('Min Power', D1)
        self.assertEqual(result.get_aggregations(), {
            'Min Power': max([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555]),
        })                

    def test_excluding_time_column(self):
        result = POWER_KPI.run('Power', D1)
        self.assertResultEqual(result, dp.Dataset({
            'Power': dp.Series([1.23 * 0.32, 5.32 * -3.2, 8.19 * 4.2555], TIMES),
        }))

    def test_mappings(self):
        '''The input Dataset should be able to map its input column names.'''
        result = POWER_KPI.run('Power', D2, {
            'Voltage': 'volts',
            'Current': 'amps',
        })
        self.assertResultEqual(result, D_POWER)

test_suite = TestKPI

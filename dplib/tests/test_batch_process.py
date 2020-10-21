from unittest import TestCase
from datetime import datetime, timedelta

from pandas._testing import assert_frame_equal
import pandas as pd

from dplib.testing import ResultAssertions
import dplib as dp

POWER = dp.KPI('Voltage * Current')
LOAD = dp.KPI('CurrentValue / MaxValue')
AT_LOAD = dp.KPI('Value if (Load >= LoadLowerBound and Load <= LoadUpperBound) else 0')

NOW = datetime.now()
TIME1 = [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)]
DF1 = dp.Dataset({
    'Voltage': dp.Series([1.23, 5.32, 8.19], TIME1),
    'Current': dp.Series([0.32, -3.2, 4.2555], TIME1),
})

TIME2 = [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
         NOW + timedelta(seconds=3), NOW + timedelta(seconds=4)]
DF2 = dp.Dataset({
    'Voltage': dp.Series([1, 2, 3, 4, 5], TIME2),
    'Current': dp.Series([3, 4, 5, 6, 7], TIME2),
})

def make_power_bp():
    return dp.BatchProcess() \
            .add('Power', POWER) \
            .add('Load %', LOAD, {
                'CurrentValue': 'Power',
                'MaxValue': 'MaxPower',
            }) \
            .add('Power at 50% Load', AT_LOAD, {
                'Load': 'Load %',
                'Value': 'Power',
                'LoadLowerBound': 0.4,
                'LoadUpperBound': 0.6,
            }) \
            .add('Power above 50% Load', AT_LOAD, {
                'Load': 'Load %',
                'Value': 'Power',
                'LoadLowerBound': 0.5,  
                'LoadUpperBound': 1.0,
            })

class TestBatchProcess(TestCase, ResultAssertions):
    def test_batch_process_get_required_inputs(self):
        bp = make_power_bp()
        inputs = bp.get_required_inputs()
        self.assertEqual(inputs, set(['Voltage', 'Current', 'MaxPower']))
        
        bp = dp.BatchProcess() \
            .add('Power', POWER) \
            .add('Other', dp.KPI('Thing * Ding'))
        inputs = bp.get_required_inputs()
        self.assertEqual(inputs, set(['Voltage', 'Current', 'Thing', 'Ding']))

        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'MyVoltage',
            })
        inputs = bp.get_required_inputs()
        self.assertEqual(inputs, set(['MyVoltage', 'Current']))
    
    def test_batch_process_prune(self):
        bp = make_power_bp()        
        self.assertEqual(bp.prune('Power at 50% Load').kpis.keys(), set(['Load %', 'Power', 'Power at 50% Load']))

        bp = dp.BatchProcess() \
            .add('A', dp.KPI('E + F')) \
            .add('B', dp.KPI('A + F'))
        self.assertEqual(bp.prune('B').kpis.keys(), set(['A', 'B']))

    def test_batch_process_dependent_kpis(self):
        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'Voltage',
                'Current': 'Current',
            }) \
            .add('Load %', LOAD, {
                'CurrentValue': 'Power',
                'MaxValue': 35,
            }) \
            .add('Power at 50% Load', AT_LOAD, {
                'Load': 'Load %',
                'Value': 'Power',
                'LoadLowerBound': 0.4,  
                'LoadUpperBound': 0.6,
            }) \
            .add('Power above 50% Load', AT_LOAD, {
                'Load': 'Load %',
                'Value': 'Power',
                'LoadLowerBound': 0.5,
                'LoadUpperBound': 1.0,
            })

        expected_result = dp.result.Result(dp.Dataset({
            'Power': dp.Series([1*3, 2*4, 3*5, 4*6, 5*7], TIME2),
            'Load %': dp.Series([1*3/35, 2*4/35, 3*5/35, 4*6/35, 5*7/35], TIME2),
            'Power at 50% Load': dp.Series([0, 0, 3*5, 0, 0], TIME2),
            'Power above 50% Load': dp.Series([0, 0, 0, 4*6, 5*7], TIME2),
        }))
            
        result = bp.run(DF2)

        self.assertResultEqual(result, expected_result)

    def test_batch_process_basic(self):
        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'Voltage',
                'Current': 'Current',
            }) \
            .add('MyVoltage', dp.KPI('X'), {
                'X': 'Voltage',
            })

        expected_result = dp.result.Result(dp.Dataset({
            'MyVoltage': dp.Series([1.23, 5.32, 8.19], TIME1),
            'Power': dp.Series([0.32 * 1.23, -3.2 * 5.32, 4.2555 * 8.19], TIME1),
        }))
            
        result = bp.run(DF1)
        self.assertResultEqual(result, expected_result)

    def test_batch_process_get_windows(self):
        bp = dp.BatchProcess() \
            .add('Window1', dp.KPI('avg(window(Signal, "2s"))'), {
                'Signal': 'Voltage',
            }) \
            .add('Window2', dp.KPI('avg(window(Signal, "8s"))'), {
                'Signal': 'Current',
            }) \
            .add('Window3', dp.KPI('avg(window(Signal, "16s")) + avg(window(Signal, "32s"))'), {
                'Signal': 'Current',
            })

        self.assertEqual(bp._get_windows(), [timedelta(seconds=2),
                                             timedelta(seconds=8),
                                             timedelta(seconds=16),
                                             timedelta(seconds=32)])

    def test_batch_process_get_max_window(self):
        bp = dp.BatchProcess() \
            .add('Window1', dp.KPI('avg(window(Signal, "2s"))'), {
                'Signal': 'Voltage',
            }) \
            .add('Window2', dp.KPI('avg(window(Signal, "8s"))'), {
                'Signal': 'Current',
            }) \
            .add('Window3', dp.KPI('avg(window(Signal, "16s")) + avg(window(Signal, "32s"))'), {
                'Signal': 'Current',
            })

        self.assertEqual(bp._get_max_window(), timedelta(seconds=32))

    def test_batch_process_graph_topological_order(self):
        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'volts',
                'Current': 'amps',
            })
        bp._connect_graph()        
        order = bp.graph.get_topological_ordering()
        self.assertEqual(order, ['Power'])

        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'volts',
                'Current': 'amps',
            }) \
            .add('Load %', LOAD, {
                'CurrentValue': 'Power',
                'MaxValue': 10000,
            }) \
            .add('Power at 50% Load', AT_LOAD, {
                'X': 'Power',
                'Load': 'Load %',
                'LoadLowerBound': 40,
                'LoadUpperBound': 60,
            })

        bp._connect_graph()        
        order = bp.graph.get_topological_ordering()
        self.assertEqual(order, ['Power', 'Load %', 'Power at 50% Load'])

        ERR_MSG = 'Batch Processes cannot contain recursive KPI computations.'

        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'Power', # Cycle
                'Current': 'amps',
            })
        with self.assertRaisesRegex(Exception, ERR_MSG):            
            bp._connect_graph()            
            bp._get_topological_ordering()
            
        bp = dp.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'volts',
                'Current': 'Power at 50% Load', # Cycle
            }) \
            .add('Load %', LOAD, {
                'CurrentValue': 'Power',
                'MaxValue': 10000,
            }) \
            .add('Power at 50% Load', AT_LOAD, {
                'X': 'Power',
                'Load': 'Load %',
                'LoadLowerBound': 40,
                'LoadUpperBound': 60,
            })
        with self.assertRaisesRegex(Exception, ERR_MSG):
            bp._connect_graph()
            bp._get_topological_ordering()
        

test_suite = TestBatchProcess

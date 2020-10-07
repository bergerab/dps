from unittest import TestCase
from datetime import datetime, timedelta
from pandas._testing import assert_frame_equal
import copy

import pandas as pd

import dplib

POWER = dplib.KPI('Voltage * Current')
LOAD = dplib.KPI('CurrentValue / MaxValue')
AT_LOAD = dplib.KPI('Value if (Load >= LoadLowerBound and Load <= LoadUpperBound) else 0')

NOW = datetime.now()

DF1 = pd.DataFrame(data={
    'Voltage': [1.23, 5.32, 8.19],
    'Current': [0.32, -3.2, 4.2555],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
})


DF2 = pd.DataFrame(data={
    'Voltage': [1, 2, 3, 4, 5],
    'Current': [3, 4, 5, 6, 7],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                  NOW + timedelta(seconds=3), NOW + timedelta(seconds=4)],
})

def make_graph_sut():
    G = dplib.Graph()
    G.connect('Power', 'Average Power')
    G.connect('Power', 'Load %')
    G.connect('Load %', 'THD Voltage at Load %')
    G.connect('THD Voltage', 'THD Voltage at Load %')
    return G

def normalize_listdict(d):
    '''
    For the Graph class, a vertex with:
    {
      'a': []
    }
    Is the same as 'a' not having any adjacent vertices.
    This function normalizes the dictionaries to reflect that (removes empty lists).
    '''
    remove = []
    for key in d:
        if d[key] == []:
            remove.append(key)
    for key in remove:
        del d[key]

def make_power_bp():
    return dplib.BatchProcess() \
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

class TestBatchProcess(TestCase, dplib.result.ResultAssertions):
    def test_batch_process_get_required_inputs(self):
        bp = make_power_bp()
        inputs = bp.get_required_inputs()
        self.assertEqual(inputs, set(['Voltage', 'Current', 'MaxPower']))
        
        bp = dplib.BatchProcess() \
            .add('Power', POWER) \
            .add('Other', dplib.KPI('Thing * Ding'))
        inputs = bp.get_required_inputs()
        self.assertEqual(inputs, set(['Voltage', 'Current', 'Thing', 'Ding']))

        bp = dplib.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'MyVoltage',
            })
        inputs = bp.get_required_inputs()
        self.assertEqual(inputs, set(['MyVoltage', 'Current']))
    
    def test_batch_process_prune(self):
        bp = make_power_bp()        
        self.assertEqual(bp.prune('Power at 50% Load').kpis.keys(), set(['Load %', 'Power', 'Power at 50% Load']))

        bp = dplib.BatchProcess() \
            .add('A', dplib.KPI('E + F')) \
            .add('B', dplib.KPI('A + F'))
        self.assertEqual(bp.prune('B').kpis.keys(), set(['A', 'B']))

    def test_graph_prune(self):
        G = dplib.Graph()
        G.connect('A', 'B')
        G.connect('B', 'C')
        
        self.assertEquals(G.prune('A').vertices, set(['A']))
        self.assertEquals(G.prune('B').vertices, set(['A', 'B']))
        self.assertEquals(G.prune('C').vertices, set(['A', 'B', 'C']))
        self.assertEquals(G.vertices, set(['A', 'B', 'C'])) # Make sure no side effects occured

        G.connect('C', 'E')
        G.connect('D', 'E')
        
        self.assertEquals(G.prune('A').vertices, set(['A']))
        self.assertEquals(G.prune('B').vertices, set(['A', 'B']))
        self.assertEquals(G.prune('C').vertices, set(['A', 'B', 'C']))
        self.assertEquals(G.prune('D').vertices, set(['D']))        
        self.assertEquals(G.prune('E').vertices, set(['A', 'B', 'C', 'D', 'E']))                
            
    def test_batch_process_dependent_kpis(self):
        bp = dplib.BatchProcess() \
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

        expected_result = dplib.result.Result(pd.DataFrame(data={
            'Power': [1*3, 2*4, 3*5, 4*6, 5*7],
            'Load %': [1*3/35, 2*4/35, 3*5/35, 4*6/35, 5*7/35],
            'Power at 50% Load': [0, 0, 3*5, 0, 0],
            'Power above 50% Load': [0, 0, 0, 4*6, 5*7],            
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2),
                          NOW + timedelta(seconds=3), NOW + timedelta(seconds=4)],
        }))
            
        result = bp.run(DF2)

        self.assertResultEqual(result, expected_result)

    def test_batch_process_basic(self):
        bp = dplib.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'Voltage',
                'Current': 'Current',
            }) \
            .add('MyVoltage', dplib.KPI('X'), {
                'X': 'Voltage',
            })

        expected_result = dplib.result.Result(pd.DataFrame(data={
            'MyVoltage': [1.23, 5.32, 8.19],
            'Power': [0.32 * 1.23, -3.2 * 5.32, 4.2555 * 8.19],
            'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
        }))
            
        result = bp.run(DF1)
        self.assertResultEqual(result, expected_result)

    def test_batch_process_get_windows(self):
        bp = dplib.BatchProcess() \
            .add('Window1', dplib.KPI('avg(window(Signal, "2s"))'), {
                'Signal': 'Voltage',
            }) \
            .add('Window2', dplib.KPI('avg(window(Signal, "8s"))'), {
                'Signal': 'Current',
            }) \
            .add('Window3', dplib.KPI('avg(window(Signal, "16s")) + avg(window(Signal, "32s"))'), {
                'Signal': 'Current',
            })

        self.assertEqual(bp._get_windows(), [timedelta(seconds=2),
                                             timedelta(seconds=8),
                                             timedelta(seconds=16),
                                             timedelta(seconds=32)])

    def test_batch_process_get_max_window(self):
        bp = dplib.BatchProcess() \
            .add('Window1', dplib.KPI('avg(window(Signal, "2s"))'), {
                'Signal': 'Voltage',
            }) \
            .add('Window2', dplib.KPI('avg(window(Signal, "8s"))'), {
                'Signal': 'Current',
            }) \
            .add('Window3', dplib.KPI('avg(window(Signal, "16s")) + avg(window(Signal, "32s"))'), {
                'Signal': 'Current',
            })

        self.assertEqual(bp._get_max_window(), timedelta(seconds=32))

    def test_batch_process_graph_topological_order(self):
        bp = dplib.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'volts',
                'Current': 'amps',
            })
        bp._connect_graph()        
        order = bp.graph.get_topological_ordering()
        self.assertEqual(order, ['Power'])

        bp = dplib.BatchProcess() \
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

        bp = dplib.BatchProcess() \
            .add('Power', POWER, {
                'Voltage': 'Power', # Cycle
                'Current': 'amps',
            })
        with self.assertRaisesRegex(Exception, ERR_MSG):            
            bp._connect_graph()            
            bp._get_topological_ordering()
            
        bp = dplib.BatchProcess() \
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
        
    def test_graph_edge_removal(self):
        G = dplib.Graph()
        G.connect('A', 'B')
        G.connect('B', 'A')
        self.assertTrue(G.has_edges())
        G.remove_edge('A', 'B')
        self.assertTrue(G.has_edges())
        G.remove_edge('B', 'A')
        self.assertFalse(G.has_edges())

    def test_graph_topological_sort_one_node(self):
        G = dplib.Graph()
        G.connect('A', 'B')
        order = G.get_topological_ordering()
        self.assertEqual(order, ['A', 'B'])
    
    def test_graph_topological_sort(self):
        G = make_graph_sut()        
        order = G.get_topological_ordering()

        # There are five possible topological orderings:
        self.assertTrue(order == ['Power', 'Load %', 'Average Power', 'THD Voltage', 'THD Voltage at Load %'] or
                        order == ['Power', 'Average Power', 'Load %', 'THD Voltage', 'THD Voltage at Load %'] or                        
                        order == ['THD Voltage', 'Power', 'Load %', 'Average Power', 'THD Voltage at Load %'] or
                        order == ['THD Voltage', 'Power', 'Average Power', 'Load %', 'THD Voltage at Load %'] or
                        order == ['THD Voltage', 'Power', 'Load %', 'THD Voltage at Load %', 'Average Power'])
        
    def test_graph_topological_sort_no_effect(self):
        '''
        Running topological sort doesn't effect the original graph (it is pure).
        '''
        G = make_graph_sut()
        
        edges_out = copy.deepcopy(G.edges_out)
        edges_in = copy.deepcopy(G.edges_in)
        vertices = G.vertices.copy()
        
        order = G.get_topological_ordering()
        self.assertEqual(normalize_listdict(G.edges_out), normalize_listdict(edges_out))
        self.assertEqual(normalize_listdict(G.edges_in), normalize_listdict(edges_in))
        self.assertEqual(G.vertices, vertices)

    def test_graph_topological_sort_throws_on_cycles(self):
        '''
        Cycles in the graph should not be allowed.
        '''
        G = make_graph_sut()
        G.connect('Power', 'Power') # Self recursive
        with self.assertRaises(dplib.CyclicGraphException):
            G.get_topological_ordering()
            
        G = make_graph_sut()
        G.connect('Load %', 'Power')
        with self.assertRaises(dplib.CyclicGraphException):
            G.get_topological_ordering()            

        # Test adding a valid edge does not cause any exception:
        G = make_graph_sut()
        G.connect('Load %', 'THD Voltage')
        G.get_topological_ordering()

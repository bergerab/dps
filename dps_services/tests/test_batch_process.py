from unittest import TestCase
from datetime import datetime, timedelta
import copy

import pandas as pd

import dplib

NOW = datetime.now()

DF1 = pd.DataFrame(data={
    'Voltage': [1.23, 5.32, 8.19],
    'Current': [0.32, -3.2, 4.2555],
    'Time': [NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)],
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

class TestBatchProcess(TestCase):
    def test_batch_process_graph_topological_order(self):
        bp = dplib.BatchProcess() \
            .add('Power', dplib.POWER, {
                'Voltage': 'volts',
                'Current': 'amps',
            }) \
            .add('Load %', dplib.LOAD, {
                'CurrentValue': 'Power',
                'MaxValue': 10000,
            }) \
            .add('Power at 50% Load', dplib.AT_LOAD, {
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
            .add('Power', dplib.POWER, {
                'Voltage': 'Power', # Cycle
                'Current': 'amps',
            })
        with self.assertRaisesRegex(Exception, ERR_MSG):            
            bp._connect_graph()            
            bp._get_topological_ordering()
            
        bp = dplib.BatchProcess() \
            .add('Power', dplib.POWER, {
                'Voltage': 'volts',
                'Current': 'Power at 50% Load', # Cycle
            }) \
            .add('Load %', dplib.LOAD, {
                'CurrentValue': 'Power',
                'MaxValue': 10000,
            }) \
            .add('Power at 50% Load', dplib.AT_LOAD, {
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
        edges = G.edges.copy()
        
        order = G.get_topological_ordering()
        self.assertEqual(normalize_listdict(G.edges_out), normalize_listdict(edges_out))
        self.assertEqual(normalize_listdict(G.edges_in), normalize_listdict(edges_in))
        self.assertEqual(G.edges, edges)

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

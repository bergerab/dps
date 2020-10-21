from unittest import TestCase

import copy

import dplib as dp
from dplib.graph import Graph

def make_graph_sut():
    G = Graph()
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
    def test_graph_edge_removal(self):
        G = Graph()
        G.connect('A', 'B')
        G.connect('B', 'A')
        self.assertTrue(G.has_edges())
        G.remove_edge('A', 'B')
        self.assertTrue(G.has_edges())
        G.remove_edge('B', 'A')
        self.assertFalse(G.has_edges())

    def test_graph_topological_sort_one_node(self):
        G = Graph()
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
        with self.assertRaises(dp.exceptions.CyclicGraphException):
            G.get_topological_ordering()
            
        G = make_graph_sut()
        G.connect('Load %', 'Power')
        with self.assertRaises(dp.exceptions.CyclicGraphException):
            G.get_topological_ordering()            

        # Test adding a valid edge does not cause any exception:
        G = make_graph_sut()
        G.connect('Load %', 'THD Voltage')
        G.get_topological_ordering()

    def test_graph_prune(self):
        G = Graph()
        G.connect('A', 'B')
        G.connect('B', 'C')
        
        self.assertEqual(G.prune('A').vertices, set(['A']))
        self.assertEqual(G.prune('B').vertices, set(['A', 'B']))
        self.assertEqual(G.prune('C').vertices, set(['A', 'B', 'C']))
        self.assertEqual(G.vertices, set(['A', 'B', 'C'])) # Make sure no side effects occured

        G.connect('C', 'E')
        G.connect('D', 'E')
        
        self.assertEqual(G.prune('A').vertices, set(['A']))
        self.assertEqual(G.prune('B').vertices, set(['A', 'B']))
        self.assertEqual(G.prune('C').vertices, set(['A', 'B', 'C']))
        self.assertEqual(G.prune('D').vertices, set(['D']))        
        self.assertEqual(G.prune('E').vertices, set(['A', 'B', 'C', 'D', 'E']))                

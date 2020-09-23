import numbers
import copy
from collections import defaultdict

import pandas as pd

from .dpl import DPL, DataSeries

class BatchProcessKPI:
    def __init__(self, name, kpi, mapping):
        self.name = name
        self.kpi = kpi
        self.mapping = mapping
        self.order = 0

class BatchProcess:
    def __init__(self):
        '''
        :param kpis:
        '''
        self.kpis = []
        self.kpi_names = set()
        self.graph = Graph()

    def add(self, name, kpi, mapping):
        self.kpi_names.add(name)
        self.kpis.append(BatchProcessKPI(name, kpi, mapping))
        return self

    def _connect_graph(self):
        for kpi in self.kpis:
            mapping = kpi.mapping
            name = kpi.name
            for ref_name in mapping.values():
                if ref_name in self.kpi_names:
                    self.graph.connect(ref_name, name)

    def _get_topological_ordering(self):
        try:
            self.graph.get_topological_ordering()
        except CyclicGraphException:
            raise Exception('Batch Processes cannot contain recursive KPI computations.')

    def run(self, time_column='Time'):
        pass

class Graph:
    def __init__(self):
        self.edges_in = defaultdict(list)
        ''' Which vertices are connected to this vertex (the key). 
            Identifies the names of vertices that have an arrow pointing at this one. 
        '''
        self.edges_out = defaultdict(list)        
        self.edges = set()

    def clone(self):
        G = Graph()
        G.edges_in = copy.deepcopy(self.edges_in)
        G.edges_out = copy.deepcopy(self.edges_out)
        G.edges = self.edges.copy()
        return G

    def connect(self, u, v):
        '''Make a connection (an edge) from node `n1` to `n2` (directed).'''
        self.edges_in[v].append(u)
        self.edges_out[u].append(v)        
        self.edges.add(u)
        self.edges.add(v)

    def get_starting_vertices(self):
        ''' Returns all vertices that have no incoming edge. '''
        edges = set()
        for edge in self.edges:
            if edge not in self.edges_in or not self.edges_in[edge]:
                edges.add(edge)
        return edges

    def remove_edge(self, u, v):
        self.edges_out[u].remove(v)
        self.edges_in[v].remove(u)

    def has_edges(self):
        for vertex, connections in self.edges_in.items():
            if connections:
                return True
        return False

    def get_topological_ordering(self):
        '''
        Kahn's Algorithm for Topological sorting
        '''
        L = []
        S = list(self.get_starting_vertices())

        restore = []

        while S:
            n = S.pop()
            L.append(n)
            out_edges = list(self.edges_out[n])
            for m in out_edges:
                self.remove_edge(n, m)
                restore.append((n, m))
                if not self.edges_in[m]:
                    S.append(m)

        has_edges = self.has_edges()

        # Restore the edges that were removed
        for (n, m) in restore:
            print(n, m)
            self.connect(n, m)
                    
        if has_edges:
            raise CyclicGraphException('Topological ordering failed because graph has at least one cycle.')

        return L

class CyclicGraphException(Exception): pass
    
'''
BatchProcess([
  POWER.map('Power', {
    'Voltage': 'volts',
    'Current': 'amps',
  }), 
  THD.map('THD (Voltage)', {
    'Signal': 'volts',
  }),
  THD.map('THD (Current)', {
    'Signal': 'amps',
  }),
 ])

TODO: How to map KPI results to KPI input

BatchProcess() \
  .add('Power', POWER, {
    'Voltage': 'volts',
    'Current': 'amps',
  }) \
  .add('THD (Voltage)', THD, {
    'Signal': 'volts',
  }) \
  .add('Load', LOAD, {
    'Max': 100000,
    'Value': 'Power',
  }) \
  .add('THD (Voltage) at 25% Load', AT_LOAD, {
    'Target': 25,
    'Value': 'THD (Voltage)',
    'Load': 'Load',
  }),
  .add('Efficiency at 25% Load', AT_LOAD, {

  }),

[
  POWER.map('Power', {
  }), 
  THD.map('THD (Voltage)', {
    'Signal': 'volts',
  }),
  THD.map('THD (Current)', {
    'Signal': 'amps',
  }),
 ])

'''

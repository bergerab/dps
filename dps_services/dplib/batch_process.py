import numbers
from collections import defaultdict

import pandas as pd

class BatchProcessKPI:
    def __init__(self, name, kpi, mapping):
        self.name = name
        self.kpi = kpi
        self.mapping = mapping

class BatchProcess:
    def __init__(self):
        '''
        :param kpis:
        '''
        self.kpis = {}
        self.graph = Graph()

    def add(self, name, kpi, mapping=None):
        mapping = {} if mapping is None else mapping
        self.kpis[name] = BatchProcessKPI(name, kpi, mapping)
        return self

    def _connect_graph(self):
        for kpi_name in self.kpis:
            kpi = self.kpis[kpi_name]
            mapping = kpi.mapping
            name = kpi.name
            self.graph.add_vertex(name)
            for ref_name in mapping.values():
                if ref_name in self.kpis.keys():
                    self.graph.connect(ref_name, name)

    def _get_topological_ordering(self):
        try:
            return self.graph.get_topological_ordering()
        except CyclicGraphException:
            raise Exception('Batch Processes cannot contain recursive KPI computations.')

    def run(self, df, time_column='Time'):
        # Topological sort the KPIs to process KPIs with no dependencies first.
        self._connect_graph()
        order = self._get_topological_ordering()

        kpis = pd.DataFrame()

        # Compute each KPI in order, adding them to the DataFrame
        for kpi_name in order:
            bpkpi = self.kpis[kpi_name]
            kpi = bpkpi.kpi
            mapping = bpkpi.mapping
            kpi_df = kpi.run(kpi_name, df.join(kpis), mapping, include_time=False)
            kpis = kpi_df.join(kpis)            

        # Return a DataFrame of only the results
        return kpis.join(df[time_column])

class Graph:
    def __init__(self):
        self.edges_in = defaultdict(list)
        ''' Which vertices are connected to this vertex (the key). 
            Identifies the names of vertices that have an arrow pointing at this one. 
        '''
        self.edges_out = defaultdict(list)        
        self.vertices = set()

    def connect(self, u, v):
        '''Make a connection (an edge) from node `n1` to `n2` (directed).'''
        self.edges_in[v].append(u)
        self.edges_out[u].append(v)        
        self.vertices.add(u)
        self.vertices.add(v)

    def add_vertex(self, name):
        '''Adds a vertex to the graph with no edges'''
        self.vertices.add(name)

    def get_starting_vertices(self):
        ''' Returns all vertices that have no incoming edge. '''
        vertices = set()
        for edge in self.vertices:
            if edge not in self.edges_in or not self.edges_in[edge]:
                vertices.add(edge)
        return vertices

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
        Kahn's Algorithm for topological sorting
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
            self.connect(n, m)
                    
        if has_edges:
            raise CyclicGraphException('Topological ordering failed because graph has at least one cycle.')

        return L

class CyclicGraphException(Exception): pass
    
'''
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

  })
'''

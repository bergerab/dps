import numbers
import copy
from collections import defaultdict

from .result import Result

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

    def prune(self, *kpi_names):
        self._connect_graph()
        bp = BatchProcess()
        bp.graph = self.graph.prune(*kpi_names)
        for kpi_name in bp.graph.vertices:
            bp.kpis[kpi_name] = self.kpis[kpi_name]
        self.graph = Graph()
        return bp

    def get_required_inputs(self):
        SEEN = set()
        s = set()
        kpis = list(self.kpis.items())
        while kpis:# kpi_name, kpi in self.kpis.items():
            kpi_name, kpi = kpis.pop()
            SEEN.add(kpi_name)
            mapping = kpi.mapping
            for id in kpi.kpi.dpl.ast.get_identifiers():
                name = id.original_name
                value = mapping.get(name)
                
                input = None
                if name not in mapping and name not in self.kpis:
                    input = id.original_name
                elif isinstance(value, str) and value not in self.kpis:
                    input = value

                print('Adding ', input, self.kpis)

                if input in self.kpis and input not in SEEN:
                    kpis.push((input, self.kpis[input]))

                if input:
                    s.add(input)
        return s

    def _connect_graph(self):
        for kpi_name in self.kpis:
            kpi = self.kpis[kpi_name]
            mapping = kpi.mapping
            name = kpi.name
            self.graph.add_vertex(name)

            dependent_kpis = set()
            for ref_name in mapping.values():
                if ref_name in self.kpis.keys():
                    dependent_kpis.add(ref_name)
            for id in kpi.kpi.dpl.ast.get_identifiers():
                if id.original_name in self.kpis.keys():
                    dependent_kpis.add(id.original_name)

            for dependent_kpi in dependent_kpis:
                self.graph.connect(dependent_kpi, name)

    def _get_topological_ordering(self):
        try:
            return self.graph.get_topological_ordering()
        except CyclicGraphException:
            raise Exception('Batch Processes cannot contain recursive KPI computations.')

    def run_all(self, df, time_column='Time', parameters=[], previous_result=None):
        '''
        Runs the batch process on the entire DataFrame (without reporting progress, one column at a time)
        '''
        # Topological sort the KPIs to process KPIs with no dependencies first.
        self._connect_graph()
        order = self._get_topological_ordering()

        input = Result.lift(df)
        result = Result()

        # Compute each KPI in order, adding them to the DataFrame
        for kpi_name in order:
            bpkpi = self.kpis[kpi_name]
            kpi = bpkpi.kpi
            mapping = bpkpi.mapping
            kpi_result = kpi.run(kpi_name, input.merge(result), mapping,
                                 include_time=False,
                                 parameters=parameters,
                                 previous_result=previous_result)
            result = kpi_result.merge(result)

        time_df = input.df[time_column].to_frame()
        result = result.merge(Result(time_df))
        if previous_result:
            result = previous_result.append(result)
        return result

    def _get_windows(self):
        '''
        Gets all the windows in the KPIs (the times in "window(x, time)")
        '''
        windows = []
        for kpi in self.kpis.values():
            windows += kpi.kpi.dpl.get_windows()
        return windows

    def _get_max_window(self):
        windows = self._get_windows()
        return max(windows)

    def _validate_windows(self):
        windows = self._get_windows()
        max_window = self._get_max_window()
        
        for window in windows:
            if max_window.total_seconds() % window.total_seconds() != 0:
                raise Exception('All windows in each KPI computation must be multiples of each other.')

    def run(self, df, time_column='Time', parameters=[], previous_result=None):
        '''
        Runs the batch process taking sub batches of the DataFrame (that have a size which is a multiple of the largest window size in the KPIs).

        For example, if there only one KPI which runs "average(window(Signal, '1s'))", this will process the DataFrame one second at a time. It will take the first second, process it, then move to the next second, until all the data has been processed.

        As another example, if there are two KPIs one which is "average(window(Signal, '1s'))" and another which is "average(window(Signal, '2s'))", this will process the DataFrame two second at a time. It will take the two second, process it, then move to the next two second, until all the data has been processed. Notice how all windows must be multiples of each other (otherwise we will get a window which is missing data).
        '''
        return self.run_all(df, time_column, parameters, previous_result)

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

    def clone(self):
        G = Graph()
        G.edges_out = copy.deepcopy(self.edges_out)
        G.edges_in = copy.deepcopy(self.edges_in)
        G.vertices = self.vertices.copy()
        return G

    def prune(self, *vertices):
        '''
        Creates a new graph that only has the vertices in `vertices` (and also all of the connections to `vertices`).
        '''
        vertices = list(vertices)
        
        G = Graph()
        for vertex in vertices:
            G.add_vertex(vertex)
        
        work_list = vertices
        while work_list:
            u = work_list.pop()
            for v in self.edges_in[u]:
                if v not in G.edges_in[u]:
                    G.connect(v, u)
            work_list += self.edges_in[u]
        return G

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

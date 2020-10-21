from .result import Result
from .exceptions import CyclicGraphException
from .graph import Graph

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
            raise CyclicGraphException('Batch Processes cannot contain recursive KPI computations.')

    def run_all(self, dataset, parameters=[], previous_result=None):
        '''
        Runs the batch process on the entire DataFrame (without reporting progress, one column at a time)
        '''
        # Topological sort the KPIs to process KPIs with no dependencies first.
        self._connect_graph()
        order = self._get_topological_ordering()

        input = Result(dataset)
        result = Result()

        # Compute each KPI in order, adding them to the DataFrame
        for kpi_name in order:
            bpkpi = self.kpis[kpi_name]
            kpi = bpkpi.kpi
            mapping = bpkpi.mapping
            kpi_result = kpi.run(kpi_name, input.merge(result), mapping,
                                 parameters=parameters,
                                 previous_result=previous_result)
            result = kpi_result.merge(result)
        if previous_result:
            result = previous_result.merge(result)
        return result

    def _get_windows(self, mappings={}):
        '''
        Gets all the windows in the KPIs (the times in "window(x, time)")
        '''
        windows = []
        for kpi in self.kpis.values():
            windows += kpi.kpi.dpl.get_windows(mappings)
        return windows

    def _get_max_window(self, mappings={}):
        windows = self._get_windows(mappings)
        if windows:
            return max(windows)
        return None

    def _validate_windows(self):
        windows = self._get_windows()
        max_window = self._get_max_window()
        
        for window in windows:
            if max_window.total_seconds() % window.total_seconds() != 0:
                raise Exception('All windows in each KPI computation must be multiples of each other.')

    def run(self, dataset, parameters=[], previous_result=None):
        '''
        Runs the batch process taking sub batches of the DataFrame (that have a size which is a multiple of the largest window size in the KPIs).

        For example, if there only one KPI which runs "average(window(Signal, '1s'))", this will process the DataFrame one second at a time. It will take the first second, process it, then move to the next second, until all the data has been processed.

        As another example, if there are two KPIs one which is "average(window(Signal, '1s'))" and another which is "average(window(Signal, '2s'))", this will process the DataFrame two second at a time. It will take the two second, process it, then move to the next two second, until all the data has been processed. Notice how all windows must be multiples of each other (otherwise we will get a window which is missing data).
        '''
        return self.run_all(dataset, parameters, previous_result)


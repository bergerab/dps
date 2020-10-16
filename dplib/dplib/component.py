from .kpi import KPI
from .batch_process import BatchProcess

class ComponentKPI:
    def __init__(self, name, kpi_string, id=None, doc=None):
        self.name = name
        self.kpi = KPI(kpi_string)
        self.id = id
        self.doc = doc

    def add_to_batch_process(self, bp, mapping):
        return bp.add(self.id, self.kpi, mapping)

class Component:
    def __init__(self, name, parameters=[]):
        self.name = name
        self.parameters = parameters
        self.kpis = {}
        self.bp = BatchProcess()

    def add(self, name, kpi_string, id=None, doc=None):
        id = id if id is not None else name
        self.kpis[name] = ComponentKPI(name, kpi_string, id, doc)
        return self

    def _validate_kpi_names(self, kpi_names):
        errors = []
        for kpi_name in kpi_names:
            if kpi_name not in self.kpis:
                errors.append(f'The "{self.name}" component has no KPI called "{kpi_name}".')
        if errors:
            raise Exception('\n'.join(errors))

    def run(self, df, kpi_names=[], mapping={}, time_column='Time', previous_result=None):
        return self.run_all(df, kpi_names, mapping, time_column, previous_result)

    def make_pruned_bp(self, kpi_names, mappings={}):
        bp = self.make_bp(mappings)
        
        kpi_ids = []
        for kpi_name in kpi_names:
            if self.kpis[kpi_name]:
                kpi_ids.append(self.kpis[kpi_name].id)
        bp = bp.prune(*kpi_ids)
        return bp

    def get_required_inputs(self, kpi_names, mappings={}):
        bp = self.make_pruned_bp(kpi_names, mappings)
        return bp.get_required_inputs()

    def make_bp(self, mapping={}):
        # Build BatchProcess for all KPIs
        bp = BatchProcess()
        for kpi in self.kpis.values():
            kpi.add_to_batch_process(bp, mapping)

        bp._connect_graph()

        return bp
        
    def run_all(self, df, kpi_names=[], mapping={}, time_column='Time', previous_result=None):
        if isinstance(kpi_names, str):
            kpi_names = [kpi_names]

        self._validate_kpi_names(kpi_names)
        bp = self.make_pruned_bp(kpi_names, mapping)
        result = bp.run(df, time_column, parameters=self.parameters, previous_result=previous_result)
        
        rename_map = {}
        kpis_in_df = list(filter(lambda x: self.kpis[x].id not in result.aggregations, kpi_names))
        for kpi_name in kpis_in_df:
            kpi = self.kpis[kpi_name]
            rename_map[kpi.id] = kpi_name

        # Filter the DataFrame so only KPIs in `kpi_names` are included
        if len(rename_map) == 0:
            result.df = None
        else:
            result.df = result.df.rename(columns=rename_map)[kpis_in_df + [time_column]]

        # Filter the aggregation dictionary so only KPIs in `kpi_names` are included
        d = {}
        for kpi_name in kpi_names:
            kpi_id = self.kpis[kpi_name].id
            if kpi_id in result.aggregations:
                d[kpi_name] = result.aggregations[kpi_id]
        result.aggregations = d

        return result

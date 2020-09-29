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

    def run(self, df, kpi_names=[], mapping={}, time_column='Time'):
        if isinstance(kpi_names, str):
            kpi_names = [kpi_names]

        self._validate_kpi_names(kpi_names)

        # Build BatchProcess for all KPIs
        bp = BatchProcess()
        for kpi in self.kpis.values():
            kpi.add_to_batch_process(bp, mapping)

        bp._connect_graph()

        # Prune BatchProcess so it only computes the necessary KPIs
        bp = bp.prune(*kpi_names)
        df = bp.run(df, time_column)
        
        rename_map = {}
        for kpi_name in kpi_names:
            kpi = self.kpis[kpi_name]
            rename_map[kpi_name] = kpi.id
        print('rename', rename_map)
        return df.rename(columns=rename_map)[kpi_names + [time_column]]

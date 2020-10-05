import numbers

import pandas as pd

from .dpl import DPL, DataSeries
from .aggregation import Aggregation
from .result import Result

class MappedKPI:
    '''
    A KPI who's KPI input values have been mapped to a DataFrame's column names.
    '''
    def __init__(self, name, env, dpl, time_column):
        self.name = name
        self.env = env
        self.dpl = dpl
        self.time_column = time_column

    def run(self, include_time, previous_result):
        x = self.dpl.run(self.env)
        return self._to_result(x, include_time, previous_result)

    def _to_result(self, x, include_time, previous_result):
        if isinstance(x, DataSeries):
            data = {
                self.name: x.to_list(),
            }
            if include_time:
                data[self.time_column] = x.get_times()
            return Result.lift(pd.DataFrame(data=data))
        elif isinstance(x, Aggregation):
            if previous_result and self.name in previous_result.aggregations:
                y = previous_result.aggregations[self.name]
                x = y.merge(x)
            return Result.lift({
                self.name: x,
            })
        else:
            raise Exception(f'KPI has invalid output type {type(x)}')

class KPI:
    '''
    A KPI computation.
    '''
    def __init__(self, code):
        self.code = code
        self.dpl = DPL()
        self.dpl.compile(code)

    def run(self, name, input, mapping={}, time_column='Time', include_time=True, parameters=[], previous_result=None):
        '''
        Create a mapping from KPI inputs to DataFrame column names, then execute the KPI immediately.

        `include_time` indicates if the resulting DataFrame should also include a time column, or just
        a single column of data (being the KPI).
        '''
        mapped_kpi = self.map(name, Result.lift(input), mapping, time_column, parameters)
        return mapped_kpi.run(include_time, previous_result)

    def map(self, name, input, mapping={}, time_column='Time', parameters=[]):
        env = self._make_environment_from_dataframe_mapping(input, mapping, time_column, parameters)
        return MappedKPI(name, env, self.dpl, time_column)

    def _make_environment_from_dataframe_mapping(self, input, mapping={}, time_column='Time', parameters=[]):
        '''
        Creates an environment to use with MiniPy from a Pandas DataFrame.

        Mapping is a function from signal name to DataFrame column, or constant name to constant value.
        For example, here is a power computation:

        KPI('Voltage * Current').run(my_df, {
            'Voltage': 'Va',
            'Current': 'Ia',
        })

        That is if `my_df` has a column named "Va" and "Ia".

        Here is an example of a constant:

        KPI('Voltage * Current * Factor').run(my_df, {
            'Voltage': 'Va',
            'Current': 'Ia',
            'Factor': 3.2,
        })

        `Factor` will be mapped to the value 3.2, "Voltage" and "Current" will come from my_df["Va"] and my_df["Ia"].

        If an identifier in the computation is not given in `mapping`,
        default to the name of the identifier.
        e.g.: with a computation of Va*Ia, and a mapping of { 'Ia': 'Current Phase A' },
              this will attempt to add an additional mapping for { 'Va': 'Va' } along with the existing one.
              Note: 'Va' might not actually exist in the input dataframe. If that is the case, an exception is thrown.
        '''
        
        errors = []
        
        env = {}

        identifiers = self.dpl.ast.get_case_sensitive_identifier_names()
        for identifier in identifiers:
            if identifier not in mapping:
                if identifier in input.df:
                    env[identifier] = DataSeries.from_df(input.df, identifier, time_column)
                elif identifier in input.aggregations:
                    env[identifier] = input.aggregations[identifier]
                else:
                    if identifier in parameters:
                        errors.append(f'You must specify the "{identifier}" parameter.')
                    else:
                        errors.append(f'Input DataFrame is missing column: "{identifier}".')
            
        for key, value in mapping.items():
            if isinstance(value, str):
                if value not in input.df:
                    errors.append(f'Input DataFrame has no column named "{value}" (when attempting to map from "{key}" to "{value}").')
                else:
                    env[key] = DataSeries.from_df(input.df, value, time_column)
            elif isinstance(value, numbers.Number):
                env[key] = value

        if errors:
            raise Exception('\n'.join(errors))
        
        return env

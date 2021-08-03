import numbers
from datetime import timedelta

import pandas as pd

from .dpl import DPL
from .series import Series
from .dataset import Dataset
from .aggregation import Aggregation
from .result import Result

class MappedKPI:
    '''
    A KPI who's KPI input values have been mapped to a Dataset's column names.
    '''
    def __init__(self, name, env, dpl):
        self.name = name
        self.env = env
        self.dpl = dpl

    def run(self, previous_result):
        x = self.dpl.run(self.env)
        return self._to_result(x, previous_result)

    def _to_result(self, x, previous_result):
        if isinstance(x, Series):
            return Result(dataset=x.to_dataset(self.name))

        if not isinstance(x, Aggregation):
            x = Aggregation(None, x)

        if previous_result and self.name in previous_result.aggregations:
            y = previous_result.aggregations[self.name]
            x = y.merge(x)
        return Result.lift({
            self.name: x,
        })

class KPI:
    '''
    A KPI computation.
    '''
    def __init__(self, code):
        self.code = code
        self.dpl = DPL()
        self.dpl.compile(code)

    def run(self, name, input, mapping={}, parameters=[], previous_result=None, cout=None):
        '''
        Create a mapping from KPI inputs to Dataset column names, then execute the KPI immediately.
        '''
        mapped_kpi = self.map(name, Result.lift(input), mapping, parameters)
        return mapped_kpi.run(previous_result)

    def map(self, name, input, mapping={}, parameters=[]):
        env = self._make_environment_from_mapping(input, mapping, parameters)
        return MappedKPI(name, env, self.dpl)

    def _make_environment_from_mapping(self, input, mapping={}, parameters=[]):
        errors = []
        env = {}

        identifiers = self.dpl.ast.get_case_sensitive_identifier_names()
        for identifier in identifiers:
            # Don't validate reserved keywords
            if identifier.lower() == 'nothing':
                continue
            if identifier not in mapping:
                if input.dataset.has(identifier):
                    env[identifier] = input.dataset.get(identifier)
                elif identifier in input.aggregations:
                    env[identifier] = input.aggregations[identifier]
                else:
                    if identifier in parameters:
                        errors.append(f'You must specify the "{identifier}" parameter.')
                    else:
                        errors.append(f'Input is missing signal: "{identifier}".')
            
        for key, value in mapping.items():
            if isinstance(value, str):
                if not input.dataset.has(value):
                    errors.append(f'Input has no signal named "{value}" (when attempting to map from "{key}" to "{value}").')
                else:
                    env[key] = input.dataset.get(value)
            elif isinstance(value, numbers.Number) or isinstance(value, timedelta):
                env[key] = value
            else:
                errors.append(f'Parameter "{key}" had an invalid type of {type(value)}.')

        if errors:
            raise Exception('\n'.join(errors))
        
        return env

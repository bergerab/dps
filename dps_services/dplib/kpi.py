import numbers

from .dpl import DPL

class KPI:
    '''
    
    '''
    def __init__(self, code):
        self.code = code
        self.dpl = DPL()
        self.dpl.compile(code)

    def run(self, df, mapping=None, time_column='Time'):
        '''
        
        '''
        env = self._make_environment_from_dataframe_mapping(df, mapping)
        return self.run(env)

    def _make_environment_from_dataframe_mapping(self, df, mapping=None, time_column='Time'):
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

        identifiers = self.ast.get_identifiers()
        for identifier in identifiers:
            if identifier not in mapping:
                if identifier not in df:
                    errors.append(f'Input DataFrame has no mapping for identifier: "{identifier}".')
                else:
                    env[identifier] = identifier
            
        for key, value in mapping.items():
            if isinstance(value, numbers.Number):
                env[key] = value
            elif isinstance(value, str):
                if value not in df:
                    errors.append(f'Input DataFrame has column named "{value}" (when attempting to map from {key} to {value}).')
                else:
                    env[key] = df[value]
            else:
                errors.append(f'Received invalid type in mapping {type(value)}')

        if errors:
            raise Exception('\n'.join(errors))
        
        return env

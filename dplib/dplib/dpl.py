import re
import numbers
from datetime import timedelta

from .minipy import MiniPy
from .data_series import DataSeries

class DPL:
    def __init__(self):
        
        def window(series, duration):
            return series.time_window(duration)
        
        def average(x):
            if isinstance(x, DataSeries):
                if x.is_windowed(): return x.average()
                else: return x.average_aggregation()
            else: raise Exception('Unsupported type for average.')
            
        def min(x):
            if isinstance(x, DataSeries):
                if x.is_windowed(): return x.min()                
                else: return x.min_aggregation()
            else: raise Exception('Unsupported type for min.')
            
        def max(x):
            if isinstance(x, DataSeries):
                if x.is_windowed(): return x.max()                
                else: return x.max_aggregation()
            else: raise Exception('Unsupported type for max.')
            
        def if_exp(test, body, orelse, env):
            test_value = test.compile().run(env)
            if isinstance(test_value, DataSeries):
                return test_value.when(body.compile().run(env), orelse.compile().run(env))
            # Otherwise, continue with normal IF behavior:
            if test_value:
                return body.compile().run(env)
            return orelse.compile().run(env)

        def thd(ds, base_harmonic, fs=None):
            if fs:
                return ds.thd2(base_harmonic, fs)
            else:
                return ds.thd(base_harmonic)
            
        self.mpy = MiniPy(builtins={
            'window': window,
            'avg': average,
            'max': max,
            'min': min,                        
            'if': if_exp,
            'thd': thd,
            'and': lambda x, y: x._and(y),
            'or': lambda x, y: x._or(y),
        })
        self.mpy.add_string_transformer(parse_time)        
        self.ast = None
        self.compiled_ast = None

    def parse(self, text):
        '''
        Parses the text to prepare it for evaluation.
        '''
        self.ast = self.mpy.parse(text)

    def compile(self, text):
        self.parse(text)
        self.compiled_ast = self.ast.compile()

    def get_windows(self):
        self.require_ast()
        sexprs = self.ast.get_sexprs()
        windows = []
        for sexpr in sexprs:
            if sexpr.name == 'WINDOW':
                windows.append(sexpr.exprs[1].x) # get the timedelta value
        return windows

    def run(self, env={}):
        '''
        Executes the last parsed text.
        '''
        self.require_ast()
        # If self.compile() has not been called, compile now.
        # Otherwise, use same compiled AST as before.
        if self.compiled_ast is None:
            self.compiled_ast = self.ast.compile()
        return self.compiled_ast.run(env)

    def require_ast(self):
        if not self.ast:
            raise Exception('You must call parse with the text of a DPL program first.')

    @staticmethod
    def eval(text, env={}):
        dpl = DPL()
        dpl.parse(text)
        return dpl.run(env)

time_pattern = re.compile('(\\d+)(ms|s|m|h|d)')
'''
Times are represented as strings of the form:
200ms -> 200 milliseconds
10s   -> 10 seconds
3m    -> 3 minutes
4h    -> 4 hours
7d    -> 4 days
'''

unit_map = {
    'ms': 'milliseconds',
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
}
'''
A mapping from shorthand names to the names timedelta uses as keywords.
'''

def parse_time(id):
    '''
    Parses a string into a timedelta value
    '''
    result = time_pattern.search(id)
    if not result: return None
    magnitude, units = result.groups()
    return timedelta(**{ unit_map[units]: int(magnitude) })

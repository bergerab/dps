import re
from datetime import timedelta

from .minipy import MiniPy

class DPL:
    def __init__(self):
        def window(series, duration):
            return series.time_window(duration)
        def average(series):
            return series.average()
        self.mpy = MiniPy(builtins={
            'window': window,
            'average': average,
        })
        self.mpy.add_string_transformer(parse_time)        
        self.ast = None

    def parse(self, text):
        '''
        Parses the text to prepare it for evaluation.
        '''
        self.ast = self.mpy.parse(text)

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
        return self.ast.compile().run(env)

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

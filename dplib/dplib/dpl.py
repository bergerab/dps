import re
import numbers
from datetime import timedelta

from .minipy import MiniPy
from .series import Series
from .builtins import BUILTINS

class DPL:
    def __init__(self):
        self.mpy = MiniPy(builtins=BUILTINS)
        self.mpy.add_string_transformer(parse_time)        
        self.ast = None
        self.compiled_ast = None

    def parse(self, text):
        '''
        Parses the text to prepare it for evaluation.
        '''
        self.ast = self.mpy.parse(text)
        return self

    def compile(self, text):
        self.parse(text)
        self.compiled_ast = self.ast.compile()
        return self

    def get_windows(self, mapping={}):
        self.require_ast()
        sexprs = self.ast.get_sexprs()
        windows = []
        for sexpr in sexprs:
            if sexpr.name == 'WINDOW':
                windows.append(sexpr.exprs[1].compile().run(mapping)) # get the timedelta value
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
        if 'Nothing' in env:
            raise Exception('Cannot set "Nothing" in environment. "Nothing" is a reserved keyword for an empty series.')
        env['Nothing'] = None
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

'''
DPL - An embedded domain specific langauge for data processing.

The language supports two kinds of computations on time-series data:
    1. Point-wise
    2. Windowed

Point-wise computations are done on each datapoint. This includes addition, 
subtraction, etc...

Windowed computations involve taking collections of datapoints and performing
some aggregation on them. This includes averaging, finding the median, total
harmonic distortion (THD), etc...

The language consists of SignalExpressions, OperatorExpressions, and WindowExpressions.
It is "compiled" into Python functions (represented by a Signal object). The purpose of the 
language is to determine which input signals are needed to perform the computation, and 
provide a more compact implementation of data processing computations.

Point-wise example:

```
Va + Vb + Vc
```

Windowed example:

```
average(window(Va, 1s))
```

Any free variables are assumed to be signal names (for example "Va" in the window example).
Durations can be expressed as identifiers such as "1s", "10ms", "2m", "12h", etc...

Computations can have either signals or constants. Constants are useful for systems which
have some rated values that have to be compared against. Signals represent direct connections
to wires in the external system.
'''

import ast
import re
from datetime import timedelta

class Expression:
    def compile(self):
        '''
        Compiles an AST of Signals, Operators, and Windows into a single Signal.
        '''
        raise Exception('compile() not implemented.')

    @staticmethod
    def compile(x):
        if isinstance(x, Expression):
            return x.compile()
        return x

class SignalExpression(Expression):
    '''
    An input signal for the computation
    '''
    def __init__(self, name):
        self.name = name
        
    def compile(self):
        '''
        Signal Expression -> Signal Value
        '''
        return value.Signal(lambda dataset: dataset[self.name])

class ConstantExpression(Expression):
    def __init__(self, name):
        self.name = name
        
    def compile(self):
        '''
        Signal Expression -> Signal Value
        '''
        return value.Signal(lambda dataset: dataset[self.name])

class ApplicationExpression(Expression):
    '''
    A point-wise computation on signals
    '''

    functions = {
        '+': lambda signals: sum(signals),
        'average': lambda args: 2
    }
    
    def __init__(self, name, exprs):
        self.name = name.lower()
        self.exprs = exprs

    def is_supported(self):
        return self.name in [
            'average',
            '+', '-', '*', '/', '//',
        ]

    def compile(self):
        '''
        Operator -> Signal
        '''
        values = map(Expression.compile, self.exprs)
        def do_signal(dataset):
            f = functions[self.name]
            return f(map(lambda value: Signal.eval(value, dataset), values))
            
        return value.Signal(do_signal)

class WindowExpression(Expression):
    '''
    A windowed computation on signals

    If window size is less than amount of data recieved, throw error.
    The caller must check the window and ensure that the given data is a multiple of the window size.
    '''
    def __init__(self, expr, size=1, stride=1):
        self.expr = expr
        self.size = size
        self.stride = stride
        
    def compile(self):
        '''
        Window -> Signal
        '''
        pass


class Signal:
    def __init__(self, f):
        '''
        f :: DataSet -> a
        '''
        self.f = f

    @staticmethod
    def eval(x, dataset):
        if isinstance(x, Signal):
            return x.f(dataset)
        return x

    def run(self, input):
        def generator():
            yield 1
        return generator

time_pattern = re.compile('(\d+)(ms|s|m|h)')
unit_map = {
    'ms': 'milliseconds',
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
}
def parse_time(id):
    result = time_pattern.search(id)
    if not result: return None
    magnitude, units = result.groups()
    return timedelta(**{ unit_map[units]: int(magnitude) })

class DPLCompiler(ast.NodeTransformer):
    def __init__(self, signal_names=[], constant_names=[]):
        self.signal_names = signal_names
        self.constant_names = constant_names
    
    def visit_Name(self, node):
        if node.id in self.signal_names:
            return ast.Call(
                func=ast.Name(id='SignalExpression', ctx=ast.Load()),
                args=[ast.Str(s=node.id)],
                keywords=[])
        if node.id in self.constant_names:
            return ast.Call(
                func=ast.Name(id='ConstantExpression', ctx=ast.Load()),
                args=[ast.Str(s=node.id)],
                keywords=[])
        return node

    def visit_Str(self, node):
        time = parse_time(node.s)
        if time:
            return ast.Call(
                func=ast.Name(id='timedelta', ctx=ast.Load()),
                args=[],
                keywords=[ast.keyword(arg='seconds', value=ast.Num(n=time.total_seconds()))])
        return node

def bytecompile_dpl(code, signal_names=[], constant_names=[]):
    code = 'global return_value;\nreturn_value = ' + code.strip('\n')
    node = ast.parse(code)
    node = DPLCompiler(signal_names, constant_names).visit(node)
    ast.fix_missing_locations(node)
    return compile(node, filename='<ast>', mode='exec')

def exec_dpl_bytecode(bytecode):
    exec(bytecode)
    return return_value

def exec_dpl(code, signal_names=[], constant_names=[]):
    return exec_dpl_bytecode(bytecompile_dpl(code, signal_names, constant_names))

if __name__ == '__main__':
    print(exec_dpl('''
Va + Vb + Vc
''', ['Va', 'Vb']))

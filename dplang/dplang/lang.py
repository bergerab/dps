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

The implementation uses Python's parser (found in the builtin ast module). It is a subset of
Python with different semantics. Computations can be made with normal operators such as '+' or
'-' for point-wise computations, and windowed computations can use the builtin functions for
'window' and 'thd'.

The language is case-insensitive to avoid issues with naming signals. This makes the difference
between 'VA', 'Va', and 'va' irrelevant.
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
        return Signal(lambda dataset: dataset[self.name])

class ConstantExpression(Expression):
    def __init__(self, name):
        self.name = name
        
    def compile(self):
        '''
        Signal Expression -> Signal Value
        '''
        return Signal(lambda dataset: dataset[self.name])

class NumberExpression(Expression):
    def __init__(self, n):
        self.n = n

    def compile(self):
        return Signal(lambda dataset: self.n)

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
'''
Times are represented as strings of the form:
200ms -> 200 milliseconds
10s   -> 10 seconds
3m    -> 3 minutes
4h    -> 4 hours
'''

unit_map = {
    'ms': 'milliseconds',
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
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

class DPLCompiler(ast.NodeVisitor):
    def __init__(self, signal_names=[], constant_names=[]):
        self.signal_names = map(lambda x: x.lower(), signal_names)
        self.constant_names = map(lambda x: x.lower(), constant_names)
        self.ast = None

    # Restrict certain statements which are not useful
    def visit_Import(self, node):
        raise Exception('Import statements are not allowed')
    def visit_Raise(self, node):
        raise Exception('Raise statements are not allowed')
    def visit_For(self, node):
        raise Exception('For statements are not allowed')
    def visit_While(self, node):
        raise Exception('While statements are not allowed')
    def visit_With(self, node):
        raise Exception('With statements are not allowed')

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Name(self, node):
        name = node.id.lower()
        if name in self.signal_names:
            return SignalExpression(node.id)
        if name in self.constant_names:
            return ConstantExpression(node.id)
        # if node is a valid function name
            # retunr the string
        raise Exception('Invalid name "' + node.id +'"')

    def visit_Str(self, node):
        time = parse_time(node.s)
        if time:
            return time
        raise Exception('Unable to parse time sting "' + node.s + '". Must be of the form: (\d+)(ms|s|m|h)')

    def visit_Num(self, node):
        return NumberExpression(node.n)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            name = '+'
        elif isinstance(op, ast.Sub):
            name = '-'
        elif isinstance(op, ast.Mult):
            name = '*'            
        elif isinstance(op, ast.Div):
            name = '/'
        elif isinstance(op, ast.FloorDiv):
            name = '//'            
        else:
            raise Exception('Unsupported BinOp')
        return ApplicationExpression(name, [left, right])

    def visit_Call(self, node):
        return ApplicationExpression(node.func.id, list(map(lambda arg: self.visit(arg), node.args)))

def parse(code, signal_names=[], constant_names=[]):
    '''
    Given some string containing DPL source code, a list of signal names, and a list of constant names,
    generates a DPL AST.
    '''
    node = ast.parse(code)
    visitor = DPLCompiler(signal_names, constant_names)
    dpl_node = visitor.visit(node)
    return dpl_node

if __name__ == '__main__':
    print(parse('''
va
''', ['Va', 'Vb', 'Vc']))

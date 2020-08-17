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

The language consists of ValueExpressions, OperatorExpressions, and WindowExpressions.
It is "compiled" into Python functions (represented by a Value object). The purpose of the 
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
have some rated values that have to be compared against. Values represent direct connections
to wires in the external system.

The implementation uses Python's parser (found in the builtin ast module). It is a subset of
Python with different semantics. Computations can be made with normal operators such as '+' or
'-' for point-wise computations, and windowed computations can use the builtin functions for
'window' and 'thd'.

The language is case-insensitive to avoid issues with naming signals. This makes the difference
between 'VA', 'Va', and 'va' irrelevant.

Example usage:

```
program = parse('Va + Vb + Vc').compile()
program.run({
'Va': DataSeries(...),
'Vb': DataSeries(...),
})
```

'''

import ast
import re
from datetime import timedelta

import functions as funcs
from main import DataSeries

class Expression:
    def compile(self):
        '''
        Compiles an AST of Values, Operators, and Windows into a single Value.
        '''
        raise Exception('compile() not implemented.')

    @staticmethod
    def compile(x):
        '''
        Compiles the given value x into a Python program.

        If the value is a DPLang Expression, it compiles the expression to a Value.
        Otherwise, just return the value as it is already compiled.
        '''
        if isinstance(x, Expression):
            return x.compile()
        return x

class IdentifierExpression(Expression):
    def __init__(self, name):
        self.name = name

    def compile(self):
        '''
        Value Expression -> Value Value
        '''
        return Value(lambda env: env.get(self.name))

class ConstantExpression(Expression):
    '''
    A constant number
    '''
    def __init__(self, x):
        self.x = x

    def compile(self):
        return Value(lambda env: self.x)

class ApplicationExpression(Expression):
    '''
    A point-wise computation on signals
    '''

    functions = {
        '+': funcs.add,
        '-': funcs.sub,
        '*': funcs.mul,
        '/': funcs.div,
        '//': funcs.floordiv,                                
        'AVERAGE': funcs.average,
        'WINDOW': funcs.window,
        'THD': lambda args: 3,
    }
    
    def __init__(self, name, exprs):
        print(name, exprs)
        self.name = name.upper()
        self.exprs = exprs

    def is_supported(self):
        return self.name.upper() in [
            'AVERAGE', 'WINDOW', 'THD',
            '+', '-', '*', '/', '//',
        ]

    def compile(self):
        '''
        Operator -> Value
        '''
        values = map(Expression.compile, self.exprs)
        def get_value(env):
            f = self.functions[self.name]
            return f(list(map(lambda value: value.run(env), values)))
            
        return Value(get_value)

class Value:
    def __init__(self, f):
        '''
        Wrapper for a function which takes an environment and returns a value.
        '''
        self.f = f

    def run(self, env):
        return self.f(Environment.lift(env))

class Environment:
    def __init__(self, env):
        self.env = {}
        for key, value in env.items():
            self.env[key.upper()] = value

    def get(self, name):
        return self.env[name.upper()]

    def set(self, name, value):
        self.env[name.upper()] = value

    @staticmethod
    def lift(x):
        if isinstance(x, Environment):
            return x
        return Environment(x)

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

class DPLVisitor(ast.NodeVisitor):
    '''
    Visits nodes in a Python AST, and builds a DPLang AST.
    '''

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
        name = node.id.upper()
        return IdentifierExpression(name)

    def visit_Str(self, node):
        time = parse_time(node.s)
        if time:
            return ConstantExpression(time)
        raise Exception('Unable to parse time sting "' + node.s + '". Must be of the form: (\d+)(ms|s|m|h)')

    def visit_Num(self, node):
        return ConstantExpression(node.n)

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
        return ApplicationExpression(node.func.id.upper(), list(map(lambda arg: self.visit(arg), node.args)))

def parse(code):
    '''
    Given some string containing DPL source code, a list of signal names, and a list of constant names,
    generates a DPL AST.
    '''
    node = ast.parse(code)
    visitor = DPLVisitor()
    dpl_node = visitor.visit(node)
    return dpl_node

if __name__ == '__main__':
    # Test point-wise computations (+ - * /)
    ds = parse('''
(va + vB + vc) / vb
''').compile().run({
    'VA': DataSeries.from_list([1, 2, 7]),
    'VB': DataSeries.from_list([3, 4, 11]),
    'VC': DataSeries.from_list([5, 6, 17]),
})
    assert ds.to_list() == [(1+3+5)/3, (2+4+6)/4, (7+11+17)/11]

    ds = parse('''
(va*vb*vc)-va
''').compile().run({
    'VA': DataSeries.from_list([1, 2, 7]),
    'VB': DataSeries.from_list([3, 4, 11]),
    'VC': DataSeries.from_list([5, 6, 17]),
})
    assert ds.to_list() == [(1*3*5)-1, (2*4*6)-2, (7*11*17)-7]

    ds = parse('''
average(window(Va, '2s'))
''').compile().run({
    'VA': DataSeries.from_list(range(10)),
})
    print(ds.to_list())

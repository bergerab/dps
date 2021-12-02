'''
MiniPy - A small feature-deprived Python style language embedded in Python

MiniPy provides:
- security
- case insensitivity
- better ergonomics

Programs can have operators, functions, and a read-only environment. There is no branching,
looping, importing, or anything else.

It isn't much different than just using Python otherwise. It is created so that
power-users can write small programs in Python via a web-server interface which
express signal processing tasks. The definition in this file is rather generic
(which is why it is called a "template"). On its own, It has nothing to do with
 data processing. But with the right identifiers in the environment,
it does.

The language provides security by being powerful enough to have arithmetic operators
and builtin functions, but not too powerful that the user can `import os` and call `rm -rf /`.
This is because the program uses its own AST and evaluation that is separate from Python.

The language is case insensitive to avoid confusion caused by differing naming conventions between
programmers and electrical engineers. For example, it might be a convention in the electrical modeling
software to have all uppercase names ~VA~, but in code to have title case ~Va~.

The language has better ergonomics by being able to define builtin identifiers. For example, you can
define an identifier `Va` in the code directly, and it will refer to some object you have passed in
the environment. This makes it look like `Va` is some builtin keyword, but it is really controled by
Python.
'''

import ast
import functools

from dplib.aggregation import Aggregation

from .exceptions import InvalidOperationException

class MiniPy:
    def __init__(self, builtins={}):
        self.builtins = { # default builtins for common operators
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '//': lambda x, y: x // y,
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            'AND': lambda x, y: x and y,
            'OR': lambda x, y: x or y,            
            'IF': lambda test, body, orelse, env: body.compile().run(env) if test.compile().run(env) else orelse.compile().run(env),
            'USUB': lambda x: -x,
        }
        for key, value in builtins.items():
            self.builtins[key.upper()] = value
        self.string_transformers = []

    def parse(self, text):
        '''
        Given some string containing MiniPy source code, generates a MiniPy AST.
        '''
        node = ast.parse(text)
        visitor = MiniPyVisitor(self, self.string_transformers)
        mpy_node = visitor.visit(node)
        return mpy_node

    def add_string_transformer(self, string_transformer):
        self.string_transformers.append(string_transformer)

class Expression:
    def compile(self):
        '''
        Compiles an AST of Readers, Operators, and Windows into a single Reader
        '''
        raise Exception('compile() not implemented.')

    @staticmethod
    def compile(x):
        '''
        Compiles the given value x into a Reader (a Python function)

        If the value is a MiniPy Expression, it compiles the expression to a Reader.
        Otherwise, just return the value as it is already compiled.
        '''
        if isinstance(x, Expression):
            return x.compile()
        return x

    def get_identifiers(self):
        '''
        Retrieves all identifiers in the expression (and all sub expressions)
        :returns: a list of :class:`Identifier`
        '''
        return []

    def get_case_sensitive_identifier_names(self):
        return list(map(lambda x: x.original_name, self.get_identifiers()))

    def get_sexprs(self):
        return []

class Identifier(Expression):
    def __init__(self, name):
        self.name = name.upper() # The case insensitive name
        self.original_name = name # The case sensitive name

    def compile(self):
        return Reader(lambda env: env.lookup(self.name))

    def get_identifiers(self):
        return [self]

class Constant(Expression):
    '''
    A constant number
    '''
    def __init__(self, x):
        self.x = x

    def compile(self):
        return Reader(lambda env: self.x)

class SExpr(Expression):
    '''
    Function application (eager left to right evaluation)
    '''
    def __init__(self, name, exprs, builtins={}):
        self.name = name.upper()
        self.exprs = exprs
        self.builtins = builtins

    def compile(self):
        values = list(map(Expression.compile, self.exprs))
        def get_value(env):
            f = self.builtins[self.name.upper()]
            xs = list(map(lambda value: value.run(env), values))
            return f(*xs)

        return Reader(get_value)

    def get_identifiers(self):
        return flatten(list(map(lambda x: x.get_identifiers(), self.exprs)))

    def get_sexprs(self):
        return [self] + flatten(list(map(lambda expr: expr.get_sexprs(), self.exprs)))

class FExpr(SExpr):
    '''
    Function application without evaluating arguments first.
    Passes in environment and unevaluated arguments.
    '''
    def compile(self):
        def get_value(env):
            f = self.builtins[self.name.upper()]
            return f(*self.exprs, env)
        return Reader(get_value)

class Reader:
    def __init__(self, f):
        '''
        Wrapper for a function which takes an environment and returns a value.
        '''
        self.f = f

    def run(self, env=None):
        env = Environment.lift(env) if env else Environment()
        return self.f(env)

class Environment:
    '''
    Computational context where there is an environment, and a set of builtins.
    '''
    def __init__(self, environment={}):
        self.environment = {}
        for key, value in environment.items():
            self.environment[key.upper()] = value

    def lookup(self, name):
        val = self.environment[name.upper()]
        if isinstance(val, Aggregation): # HACK :( was a quick way to fix a bad bug where aggregations got merged too often. If you had an agg that used another agg and you had more than one batch, you got a double merge.
            val = val.clone()
            val.skip_merge = True
        return val

    @staticmethod
    def lift(x):
        if isinstance(x, Environment):
            return x
        return Environment(x)

class MiniPyVisitor(ast.NodeVisitor):
    '''
    Visits nodes in a Python AST, and builds a MiniPy AST.
    '''
    def __init__(self, mpy, string_transformers):
        self.mpy = mpy
        self.string_transformers = string_transformers

    # Restrict certain statements which are not useful
    def visit_Import(self, node):
        raise InvalidOperationException('Import statements are not allowed')
    def visit_Raise(self, node):
        raise InvalidOperationException('Raise statements are not allowed')
    def visit_For(self, node):
        raise InvalidOperationException('For statements are not allowed')
    def visit_While(self, node):
        raise InvalidOperationException('While statements are not allowed')
    def visit_With(self, node):
        raise InvalidOperationException('With statements are not allowed')

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Name(self, node):
        return Identifier(node.id)

    def visit_UnaryOp(self, node):
        op = node.op
        operand = node.operand
        if isinstance(op, ast.USub):
            return SExpr('USUB', [self.visit(operand)], self.mpy.builtins)
        else:
            raise Exception('Unsupported BinOp')

    def visit_Str(self, node):
        for string_transformer in self.string_transformers:
            result = string_transformer(node.s)
            if result is not None:
                return Constant(result)
        return Constant(node.s)

    def visit_Num(self, node):
        return Constant(node.n)

    def visit_IfExp(self, node):
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        return FExpr('IF', [test, body, orelse], self.mpy.builtins)

    def visit_BoolOp(self, node):
        values = list(map(lambda x: self.visit(x), node.values))
        op = node.op
        if isinstance(op, ast.And):
            name = 'and'
        elif isinstance(op, ast.Or):
            name = 'or'
        else:
            raise Exception('Unsupported boolean operator.')
        return SExpr(name, values, self.mpy.builtins)        

    def visit_Compare(self, node):
        if len(node.ops) > 1:
            raise Exception('MiniPy does not support multiple comparisons in one expression')
        if len(node.comparators) > 1:
            raise Exception('MiniPy does not support multiple comparators in one comparison expression')
        left = self.visit(node.left)
        comparator = self.visit(node.comparators[0])
        op = node.ops[0]
        if isinstance(op, ast.Gt):
            name = '>'
        elif isinstance(op, ast.Lt):
            name = '<'
        elif isinstance(op, ast.GtE):
            name = '>='
        elif isinstance(op, ast.LtE):
            name = '<='
        elif isinstance(op, ast.Eq):
            name = '=='
        elif isinstance(op, ast.NotEq):
            name = '!='
        else:
            raise Exception('Unsupported comparison')
        return SExpr(name, [left, comparator], self.mpy.builtins)        

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
        return SExpr(name, [left, right], self.mpy.builtins)

    def visit_Call(self, node):
        return SExpr(node.func.id.upper(), list(map(lambda arg: self.visit(arg), node.args)), self.mpy.builtins)

def flatten(xs):
    if not xs:
        return xs
    return functools.reduce(
        lambda a, b: a + b, xs)

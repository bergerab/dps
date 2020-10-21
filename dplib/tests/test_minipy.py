from unittest import TestCase

from dplib.minipy import MiniPy, InvalidOperationException

def run(text, env={}, builtins={}, modify=lambda x:x):
    mpy = MiniPy(builtins)
    modify(mpy)
    return mpy.parse(text).compile().run(env)

class TestMiniPy(TestCase):
    def test_basic(self):
        '''
        Basic evaluation
        '''
        self.assertEqual(run('1'), 1)
        self.assertEqual(run('-1'), -1)
        self.assertEqual(run('"a"'), "a")
    
    def test_operators(self):
        '''
        The arithmetic operators + - * / and // should be supported, and should call
        the object's dunder methods (__add__, __sub__, etc...)

        Same with the comparison operators < > <= >= == !=

        Order of operations should be preserved, and parenthesis should be supported.
        '''
        # Arithmetic operators
        self.assertEqual(run('9 + 2'), 9 + 2)
        self.assertEqual(run('11 - 6'), 11 - 6)
        self.assertEqual(run('7 * 13'), 7 * 13)
        self.assertEqual(run('7 / 17'), 7 / 17)
        self.assertEqual(run('70 // 27'), 70 // 27)

        # Comparison operators
        self.assertEqual(run('83 < -2'), 83 < -2)
        self.assertEqual(run('-2 < 82'), -2 < 82)
        self.assertEqual(run('83 > -2'), 83 > -2)
        self.assertEqual(run('-2 > 82'), -2 > 82)
        self.assertEqual(run('83 >= -2'), 83 >= -2)
        self.assertEqual(run('-2 >= 82'), -2 >= 82)
        self.assertEqual(run('83 <= -2'), 83 <= -2)
        self.assertEqual(run('-2 <= 82'), -2 <= 82)
        self.assertEqual(run('-2 == -2'), -2 == -2)
        self.assertEqual(run('-82 == -2'), -82 == -2)        
        self.assertEqual(run('-2 != -2'), -2 != -2)
        self.assertEqual(run('-82 != -2'), -82 != -2)        

        # operators can be used with non-numeric types
        self.assertEqual(run('"a" + "b"'), 'ab')

        # order of operations is equivalent to Python's
        self.assertEqual(run('9 - 3 * 2'), 9 - 3 * 2)
        self.assertEqual(run('(2 + 11) * (8 / 2)'), (2 + 11) * (8 / 2))

    def test_IfExp(self):
        # True case
        self.assertEqual(run('3 if 1 else 2'), 3)
        # False case
        self.assertEqual(run('3 if 0 else 2'), 2)
        # Nested false case
        self.assertEqual(run('3 if (1 if 0 else 0) else 2'), 2)

        # Test that the IF builtin can be set to modify the semantics
        def backwards_if_exp(test, body, orelse, env):
            '''
            An if expression, but when the test is true the orelse block is evaluated
            and when the test is false, the body is evaluated.
            '''
            if test.compile().run(env):
                return orelse.compile().run(env)
            else:
                return body.compile().run(env)
        self.assertEqual(run('"b" if 1 else "a"', builtins={ 'IF': backwards_if_exp }), "a")
        self.assertEqual(run('"b" if 0 else "a"', builtins={ 'IF': backwards_if_exp }), "b")

    def test_environment(self):
        '''
        Variables should be able to be bound via Python and properly looked up during runtime.
        '''
        self.assertEqual(run('a + 7', { 'a': 8 }), 7 + 8)
        self.assertEqual(run('a + b', { 'a': 19, 'b': -3 }), 19 + -3)
        self.assertEqual(run('a + b', { 'a': 'sdf', 'b': 'ieo' }), 'sdf' + 'ieo')

    def test_builtins(self):
        '''
        Allow for passing builtin functions as a parameter.
        '''
        self.assertEqual(run('rightplusone(9, 3)', {}, { 'rightplusone': lambda x, y: y + 1 }), 3+1)
        self.assertEqual(run('threeargs(9, 2, 8)', {}, { 'threeargs': lambda x, y, z: x + y - z }), 9 + 2 - 8)
        self.assertEqual(run('onearg(83)', {}, { 'onearg': lambda x: x+7 }), 83 + 7)

    def test_builtins_override(self):
        '''
        Allow for overriding of builtins (even the builtin operators like +).
        '''
        self.assertEqual(run('39 * 291', {}, { '+': lambda xs: xs[0] * xs[1] }), 39 * 291)

    def test_string_transformers(self):
        '''
        String transformers should allow for replacing string literals with other constants, and be skipped by returning `None`.

        MiniPy should process string transformers one by one, and use the first one that matches
        If there are no matches, the string literal should be used as theee value
        '''
        def modify_string_to_constant(s, n):
            def modify(mpy):
                mpy.add_string_transformer(lambda x: n if x == s else None)
            return modify
        def modify_string_to_constant2(s1, n1, s2, n2):
            def modify(mpy):
                mpy.add_string_transformer(lambda x: n1 if x == s1 else None)
                mpy.add_string_transformer(lambda x: n2 if x == s2 else None)                
            return modify
        self.assertEqual(run('"teststring"', {}, modify=modify_string_to_constant("teststring", 8339)), 8339)

        self.assertEqual(run('"b"', {}, modify=modify_string_to_constant2("a", 82, "b", 93)), 93)
        self.assertEqual(run('"a"', {}, modify=modify_string_to_constant2("a", 82, "b", 93)), 82)
        self.assertEqual(run('"c"', {}, modify=modify_string_to_constant2("a", 82, "b", 93)), 'c')                        

    def test_identifier_casing(self):
        '''
        All identifiers for variables should be case insensitive.
        '''
        self.assertEqual(run('test', { 'test': 293 }), 293)
        self.assertEqual(run('Test', { 'test': 11 }), 11)
        self.assertEqual(run('TEST', { 'test': 83 }), 83)
        self.assertEqual(run('TEST', { 'TEST': 144 }), 144)
        self.assertEqual(run('TEST', { 'Test': 812 }), 812)
        self.assertEqual(run('teSt', { 'TeST': 993 }), 993)

    def test_builtin_identifier_casing(self):
        '''
        All identifiers for builtins should be case insensitive.
        '''
        self.assertEqual(run('testmod(11, 3)', {}, { 'testmod': lambda x, y: x % y }), 11 % 3)
        self.assertEqual(run('TestMod(93, 12)', {}, { 'testmod': lambda x, y: x % y }), 93 % 12)
        self.assertEqual(run('testMOD(80, 20)', {}, { 'TEsTMod': lambda x, y: x % y }), 80 % 20)                                                                        
    def test_security(self):
        '''
        Normal Python functionality is disallowed.

        Imports and loops (which could be infinite) should cause an error to be thrown.

        Note that any statements that ARE allowed but do not throw an exception are still acceptable.
        Its just that they will be ignored during evaluation. It is better that an exception is raised so the user is aware that the language doesn't support that keyword, instead of silently ignoring the keyword.
        '''
        with self.assertRaises(InvalidOperationException):
           run('import os')
        with self.assertRaises(InvalidOperationException):
            run('while True: pass')
        with self.assertRaises(InvalidOperationException):
            run('for x in range(100000000000): pass')
        with self.assertRaises(InvalidOperationException):
            run('with x as y: pass')
        with self.assertRaises(InvalidOperationException):
            run('raise Exception("test")')

    def test_get_identifiers(self):
        ids_to_set = lambda xs: {x for x in map(lambda x: x.name, xs)}

        mpy = MiniPy()

        # No identifiers
        ids = mpy.parse('2').get_identifiers()
        self.assertEqual(len(ids_to_set(ids)), 0)

        # One identifier
        ids = mpy.parse('de').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'DE'})

        # Two identifiers
        ids = mpy.parse('VA + VB').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'VA', 'VB'})

        # Resulting identifiers should be case insensitive (always uppercased)
        ids = mpy.parse('vA + VB').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'VA', 'VB'})

        # Three identifiers with noise (parenthesis)
        ids = mpy.parse('((vA + VB)+ neww)').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'VA', 'VB', 'NEWW'})

        # Applications should extract identifiers
        ids = mpy.parse('((fcall(vA) + vcc)+ call2(neww))').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'VA', 'VCC', 'NEWW'})

        # Nested applications should extract identifiers
        ids = mpy.parse('((fcall(arg1, arg2, ie(arg3, wo(arg4))) + vcc)+ call2(neww))').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'ARG1', 'ARG2', 'ARG3', 'ARG4', 'VCC', 'NEWW'})

        # If expressions should extract identifiers
        ids = mpy.parse('((fcall(arg1 if unicorn else donkey, arg2, ie(arg3, wo(arg4))) + vcc)+ call2(neww))').get_identifiers()
        self.assertEqual(ids_to_set(ids), {'ARG1', 'UNICORN', 'DONKEY', 'ARG2', 'ARG3', 'ARG4', 'VCC', 'NEWW'})

    def test_logical_operators(self):
        self.assertEqual(run('1 and 2'), 2)
        self.assertEqual(run('1 > 0 and 2 > 0'), True)
        self.assertEqual(run('1 < 0 or 2 > 0'), True)

test_suite = TestMiniPy

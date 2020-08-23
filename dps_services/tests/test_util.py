from unittest import TestCase
from datetime import datetime, timedelta

import dps_services.util as util

from numbers import Number

class TestUtil(TestCase):
    def test_quoted(self):
        self.assertEqual(util.quoted('a'), '"a"')
        self.assertEqual(util.quoted(123), '"123"')
        self.assertEqual(util.quoted(123, n=1), '"1"')
    
    def test_request_validator(self):
        d = {
            'a': 1,
            'b': 'hi',
            'c': [{
                'animal': 'dog'
            }, {
                'animal': 'cat'
            }],
            'e': 3.14,
            'f': {
                'g': 3
            }
        }
        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "d".'):
            with util.RequestValidator(d) as validator:
                validator.require('d')
        with util.RequestValidator(d) as validator:
            validator.require('a')

        with self.assertRaisesRegex(util.ValidationException, 'Expected str type, but received int type for parameter "a".'):
            with util.RequestValidator(d) as validator:
                validator.require('a', str)

        with self.assertRaisesRegex(util.ValidationException, 'Expected parameter "b" to be either "hello", "hola" or "wow", but was "hi".'):
            with util.RequestValidator(d) as validator:
                validator.require('b', str, one_of=['hello', 'hola', 'wow'])

        with self.assertRaisesRegex(util.ValidationException, 'Expected parameter "b" to be "stink", but was "hi".'):
            with util.RequestValidator(d) as validator:
                validator.require('b', str, one_of=['stink'])

        with util.RequestValidator(d) as validator:
            validator.require('a', int)

        with util.RequestValidator(d) as validator:
            validator.require('o', int, optional=True)
            validator.require('o', optional=True)
            validator.require('a', optional=True)
            validator.require('a', int, optional=True)

        with util.RequestValidator(d) as validator:
            c = validator.require('c', list, default=[])
            for i, value in enumerate(c):
                with validator.scope_list('c', i):
                    validator.require('animal', required_type=str, one_of=['cat', 'dog'])
        with util.RequestValidator(d) as validator:
            c = validator.require('c', list, default=[])
            for i, value in enumerate(c):
                with validator.scope_list('c', i):
                    validator.require('animal', required_type=str)

        with self.assertRaisesRegex(util.ValidationException, 'Expected int type, but received str type for parameter "c\[0\].animal".\nExpected int type, but received str type for parameter "c\[1\].animal".'):                    
            with util.RequestValidator(d) as validator:
                c = validator.require('c', list, default=[])
                for i, value in enumerate(c):
                    with validator.scope_list('c', i):
                        validator.require('animal', required_type=int)
            
        with util.RequestValidator(d) as validator:            
            validator.require('a', Number)
            
        with util.RequestValidator(d) as validator:            
            validator.require('e', Number)
        
        with self.assertRaisesRegex(util.ValidationException, 'Request is missing required parameter "f.h".'):
            with util.RequestValidator(d) as validator:
                with validator.scope('f'):
                    validator.require('h')

        # The error message includes all validation errors
        with self.assertRaisesRegex(util.ValidationException, 'Expected str type, but received int type for parameter "a".\nRequest is missing required parameter "f.h".'):
            with util.RequestValidator(d) as validator:
                validator.require('a', str)                
                with validator.scope('f'):
                    validator.require('h')

    def test_make_api_url(self):
        self.assertEqual(util.make_api_url('a'), '/api/v1/a')
        self.assertEqual(util.make_api_url('a', version=2), '/api/v2/a')
        self.assertEqual(util.make_api_url('boop', version=3), '/api/v3/boop')

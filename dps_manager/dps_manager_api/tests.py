from unittest import TestCase
from datetime import datetime, timedelta

from .models import SystemSerializer
from .util import Diff

class TestSerializers(TestCase):
    def test_kpi(self):
        self.assertFalse(KPISerializer(data={
                             'name': 'Dink',
                        }).is_valid())

        self.assertTrue(KPISerializer(data={
            'name': 'Dink',
            'identifier': 'di',
            'computation': 'A + B',
            'description': 'Sum of A and B.',
            'hidden': False,
        }).is_valid())

        self.assertTrue(KPISerializer(data={
            'name': 'Dink',
            'identifier': 'di',
            'computation': 'A + B',
            'description': 'Sum of A and B.',
            # Hidden is optional
        }).is_valid(), '"hidden" should be optional')

        self.assertTrue(KPISerializer(data={
            'name': 'Dink',
            # Identifier is optional
            'computation': 'A + B',
            'description': 'Sum of A and B.',
            # Hidden is optional
        }).is_valid(), '"identifier" should be optional')

        self.assertTrue(KPISerializer(data={
            'name': 'Dink',
            # Identifier is optional
            'computation': 'A + B',
            # Description is optional
            # Hidden is optional
        }).is_valid(), '"description" should be optional')

    def test_system(self):
        self.assertTrue(SystemSerializer(data={
            'name': 'My System',
        }).is_valid(), 'Systems should only require a name.')
        
        self.assertFalse(SystemSerializer(data={
            'parameters': []
        }).is_valid(), 'Systems must have a name.')

        self.assertTrue(SystemSerializer(data={
            'name': 'My System',
            'parameters': ['a'],            
        }).is_valid(), 'Systems can have one parameter.')
        
        self.assertTrue(SystemSerializer(data={
            'name': 'My System',
            'parameters': ['1', '3'],
            'kpis': [{
                'name': 'KPI1',
                'computation': 'A + B',
            }, {
                'name': 'KPI2',
                'computation': 'avg(C)',
            }],
        }).is_valid(), 'Systems can have KPI objects.')

class TestSerializers(TestCase):
    def test_same(self):
        d = Diff([1, 2, 3],
                 [1, 2, 3])
        self.assertEqual(d.get_unchanged(), {1, 2, 3})
        self.assertEqual(d.get_deletions(), set())
        self.assertEqual(d.get_additions(), set())

    def test_delete(self):
        d = Diff([1, 2, 3],
                 [1, 3])
        self.assertEqual(d.get_unchanged(), {1, 3})
        self.assertEqual(d.get_deletions(), {2})
        self.assertEqual(d.get_additions(), set())

    def test_add(self):
        d = Diff([1, 2, 3],
                 [1, 3, 5])
        self.assertEqual(d.get_unchanged(), {1, 3})
        self.assertEqual(d.get_deletions(), {2})
        self.assertEqual(d.get_additions(), {5})

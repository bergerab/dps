from unittest import TestCase
from nose.plugins.attrib import attr


@attr('database_manager', type='integration')
class TestDatabaseManagerIntegration(TestCase):
    def test_fail(self):
        self.assertEqual(1, 0)

from unittest import TestCase
from nose.plugins.attrib import attr

@attr('database_manager', type='integration')
class TestDatabaseManagerIntegration(TestCase):
    pass

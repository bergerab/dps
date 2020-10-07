from datetime import datetime
import unittest

def make_test_case(client):
    class TestDPSManager(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super(TestDPSManager, self).__init__(*args, **kwargs)
            self.maxDiff = None
        
        def validate_status_code(self, response):
            if response.status_code != 200:
                print(response.json())
            self.assertEqual(response.status_code, 200)

        

    return TestDatabaseManager

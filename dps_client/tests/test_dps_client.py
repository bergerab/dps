from unittest import TestCase

import dps_client as dpsc

class TestDPSClient(TestCase):
    def test_normalize_url(self):
        self.assertEqual(dpsc._normalize_url('http://localhost/oijwef'), 'http://localhost/oijwef/')
        self.assertEqual(dpsc._normalize_url('http://localhost/oijwef/'), 'http://localhost/oijwef/')

    def test_(self):
        pass

from unittest import TestCase
from datetime import datetime, timedelta

from dplib import KPI

class TestKPIs(TestCase):
    def test_three_phase_power(self):
        '''Tests Va*Ia + Vb*Ib + Vc*Ic'''
        three_phase_power = KPI('Va*Ia + Vb*Ib + Vc*Ic')

import numbers
from itertools import defaultdict
from functools import flatten

import pandas as pd

from .dpl import DPL, DataSeries

class BatchProcessKPI:
    def __init__(self, name, kpi, mapping):
        self.name = name
        self.kpi = kpi
        self.mapping = mapping
        self.order = 0

class BatchProcess:
    '''
    TODO: Throw exception for recursive KPIs and mutually recursive KPIs.
    Example: Y is Z+A and Z is Y+A.
    '''
    def __init__(self):
        '''
        :param kpi_list:
        '''
        self.kpi_list = []

    def add(self, name, kpi, mapping):
        self.kpis.append(BatchProcessKPI(name, kpi, mapping))

    def run(self, time_column='Time'):
        pass

'''
BatchProcess([
  POWER.map('Power', {
    'Voltage': 'volts',
    'Current': 'amps',
  }), 
  THD.map('THD (Voltage)', {
    'Signal': 'volts',
  }),
  THD.map('THD (Current)', {
    'Signal': 'amps',
  }),
 ])

TODO: How to map KPI results to KPI input

BatchProcess() \
  .add('Power', POWER, {
    'Voltage': 'volts',
    'Current': 'amps',
  }) \
  .add('THD (Voltage)', THD, {
    'Signal': 'volts',
  }) \
  .add('Load', LOAD, {
    'Max': 100000,
    'Value': 'Power',
  }) \
  .add('THD (Voltage) at 25% Load', AT_LOAD, {
    'Target': 25,
    'Value': 'THD (Voltage)',
    'Load': 'Load',
  }),
  .add('Efficiency at 25% Load', AT_LOAD, {

  }),

[
  POWER.map('Power', {
  }), 
  THD.map('THD (Voltage)', {
    'Signal': 'volts',
  }),
  THD.map('THD (Current)', {
    'Signal': 'amps',
  }),
 ])

'''

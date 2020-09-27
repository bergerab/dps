from .kpi import KPI

'''
General Purpose KPIs
'''

ONE_PHASE_POWER = POWER = KPI('Voltage * Current')
'''
Power for single phase voltage (`Voltage`) and current (`Current`).
'''

THREE_PHASE_POWER = KPI('Va * Ia + Vb * Ib + Vc * Ic')
'''
Power for three phase voltage (`Va`, `Vb`, `Vc`) and current (`Ia`, `Ib`, `Ic`).
'''

LOAD = KPI('CurrentValue / MaxValue')
'''
Load Percent (as a decimal)

Divides the CurrentValue of the load by the MaxValue.
'''

AT_LOAD = KPI('Value if (Load >= LoadLowerBound and Load <= LoadUpperBound) else 0')
'''
A snapshot of a signal when the load is between two values.

Take `Value`'s value when the `Load` is between `LoadLowerBound` and 
`LoadUpperBound` otherwise use zero as the value.

For computing THD at load percentages, and components of weighted efficiency.
'''

EFFICIENCY = KPI('Output / Input')
'''
How much output per unit of input.
'''

THD = KPI('thd(window(Signal, "1s"), BaseHarmonic)')
'''
THD with one second resolution.
'''

'''
PV Array KPIs
'''

FILL_FACTOR = KPI('Pmax / (Voc * Isc)')
'''
Measures the quality of a solar cell.

A reasonable value for Voc and Isc are:
Voc = 520V
Isc = 970 (units?)
'''

PV_EFFICIENCY = KPI('(Idc * Vdc) / (A * S)')
PV_MAX_EFFICIENCY = KPI('(Voc * Isc * FF) / (A * S)')

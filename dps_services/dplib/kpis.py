from .kpi import KPI

ONE_PHASE_POWER = POWER = KPI('Voltage * Current')
THREE_PHASE_POWER = KPI('Va*Ia + Vb*Ib + Vc*Ic')

LOAD = KPI('CurrentValue / MaxValue')

AT_LOAD = KPI('X if Load >= LoadLowerBound and Load <= LoadUpperBound else 0')

from .kpi import KPI

ONE_PHASE_POWER = POWER = KPI('Voltage * Current')
THREE_PHASE_POWER = KPI('Va*Ia + Vb*Ib + Vc*Ic')


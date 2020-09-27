from .component import Component
from .kpi import KPI

PVArray = Component('PV Array',
                parameters=['Voc', 'Isc']) \
            .add('FillFactor',
                 '(Imp * Vmp) / (Voc * Isc)',
                 display_name= 'Fill Factor',
                 doc='Measures of the quality of the solar cell.') \
            .add('Efficiency',
                 '(Idc * Vdc) / (A * S)',
                 doc='The ratio of the electrical power output (Pout), compared to the solar power input of the PV cell.') \
            .add('MaxEfficiency',
                 '(Voc * Isc * FillFactor) / (A * S)',
                 display_name='Max Efficiency',
                 doc='The ratio of the electrical max power output (Pmax), compared to the solar power input of the PV cell.')

PVInverter = Component('PV Array Inverter',
    parameters=['THDBaseHarmonic']) \
    .add('THD Va', 'THD_Va', make_thd('Va')) \
    .add('THD Vb', 'THD_Vb', make_thd('Vb')) \
    kpis={
        'Efficiency': '(Va*Ia + Vb*Ib + Vc*Ic) / (Imp * Vmp)',
        'WeightedEfficiency': '''
            (0.04 * (Efficiency if Load >= 5 and Load <= 15 else 0)) +
            (0.05 * (Efficiency if Load >= 15 and Load <= 20 else 0)) +    
            (0.12 * (Efficiency if Load >= 25 and Load <= 35 else 0)) +    
            (0.21 * (Efficiency if Load >= 45 and Load <= 55 else 0)) +    
            (0.53 * (Efficiency if Load >= 70 and Load <= 80 else 0)) +    
            (0.05 * (Efficiency if Load >= 95 else 0))
        ''',
    })
add_thds(PVInverter, 'Va', 'Vb', 'Vc', 'Ia', 'Ib', 'Ic')

def add_thds(component, *names):
    for name in names:
        component.add(f'THD_{name}', f'thd(window({name}, "1s"), THDBaseHarmonic)', display_name=f'THD {name}')

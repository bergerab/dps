from .component import Component
from .kpi import KPI


def PVArray():
    return Component('PV Array',
                parameters=['Voc', 'Isc']) \
            .add('Fill Factor',
                 '(Imp * Vmp) / (Voc * Isc)',
                 doc='Measures of the quality of the solar cell.') \
            .add('Efficiency',
                 '(Idc * Vdc) / (A * S)',
                 doc='The ratio of the electrical power output (Pout), compared to the solar power input of the PV cell.') \
            .add('Max Efficiency',
                 '(Voc * Isc * FillFactor) / (A * S)',
                 doc='The ratio of the electrical max power output (Pmax), compared to the solar power input of the PV cell.')

def PVInverter():
    component = Component('PV Array Inverter',
        parameters=['THDBaseHarmonic']) \
        .add('Efficiency', '(Va*Ia + Vb*Ib + Vc*Ic) / (Imp * Vmp)') \
        .add('Weighted Efficiency', '''
            (0.04 * (Efficiency if Load >= 5 and Load <= 15 else 0)) +
            (0.05 * (Efficiency if Load >= 15 and Load <= 20 else 0)) +    
            (0.12 * (Efficiency if Load >= 25 and Load <= 35 else 0)) +    
            (0.21 * (Efficiency if Load >= 45 and Load <= 55 else 0)) +    
            (0.53 * (Efficiency if Load >= 70 and Load <= 80 else 0)) +    
            (0.05 * (Efficiency if Load >= 95 else 0))
        ''')
    add_thds(component, 'Va', 'Vb', 'Vc', 'Ia', 'Ib', 'Ic')
    return component

def DieselGenerator():
    return Component('Diesel Generator',
            parameters=[]) \
            .add('Fuel Consumption', 'average(window(FuelConsumption, "1s"))',
                 doc='Average fuel consumption (every second).') \
            .add('Generator Efficiency', '') # TODO: Continue for second Word doc of KPIs

def add_thds(component, *names):
    '''
    Adds a THD computation for each signal name (and THD at load percentages).
    '''
    for name in names:
        component.add(f'THD_{name}', f'thd(window({name}, "1s"), THDBaseHarmonic)',
                      display_name=f'THD {name}')
        component.add(f'THD {name} at 25% Load', f'THD_{name} if LOAD >= 20 and LOAD <= 30 else 0')
        component.add(f'THD {name} at 50% Load', f'THD_{name} if LOAD >= 45 and LOAD <= 55 else 0')
        component.add(f'THD {name} at 75% Load', f'THD_{name} if LOAD >= 70 and LOAD <= 80 else 0')
        component.add(f'THD {name} at 100% Load', f'THD_{name} if LOAD >= 95 else 0')        

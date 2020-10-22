'''
This file is used to generate a CSV for main.py.
'''
import numpy as np
import pandas as pd
import random

from datetime import datetime, timedelta

import dplib.testing as dpt

def generate_sine_wave(t0=0, periods=2, offset=0.0, dt=1e-5, amplitude=2, base_harmonic=40):
    '''
    Generate discrete samples of a pure sine wave.
    '''
    cycles = 0.025*periods
    N = int((cycles-t0)/dt)
    time = np.linspace(0.0, cycles, N)
    return [time, amplitude*np.sin(2.0*np.pi*base_harmonic*time) + offset]

def write_csv(verbose=False):
    if verbose:
        print('Generating current signal...')
    current = dpt.WaveGenerator() \
        .add(frequency=30, amplitude=30) \
        .generate(sample_rate=5000, duration=5)
    if verbose:
        print('Generating voltage signal...')
    voltage = dpt.WaveGenerator() \
        .add(frequency=30, amplitude=200, phase_shift=np.pi/2) \
        .generate(sample_rate=5000, duration=5)

    if verbose:
        print('Generating distorted voltage signal...')
    voltage_with_distortion = dpt.WaveGenerator() \
        .add(frequency=30, amplitude=30) \
        .add(frequency=30*2, amplitude=10) \
        .generate(sample_rate=5000, duration=5)

    NOW = datetime.now()
    
    if verbose:
        print('Generating DataFrame...')        
    df = pd.DataFrame(data={
        # Two AC signals
        'AC_Voltage': voltage.get_signal(),
        'Distorted AC_Voltage': voltage_with_distortion.get_signal(),        
        'AC_Current': current.get_signal(),
        
        # Example of a DC circuit ramping-up a voltage signal from 0 to 50,000
        # With a fixed current of ~10
        'DC_Voltage': map(lambda x: 50000 * (x/len(voltage.get_signal())), range(len(voltage.get_signal()))),
        'DC_Current': map(lambda x: 10 - random.random(), range(len(voltage.get_signal()))),                
        'Time': current.get_times(),
    })
    if verbose:
        print('Writing CSV...')            
    df.to_csv('data.csv')
    if verbose:
        print('Done, wrote Dataframe!')
        print(df)

if __name__ == '__main__':
    write_csv(True)

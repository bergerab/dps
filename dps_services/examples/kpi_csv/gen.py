'''
This file is used to generate a CSV for main.py.
'''
import numpy as np
import pandas as pd
import random

from datetime import datetime, timedelta

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
        print('Generating voltage signal...')
    time, Voltage = generate_sine_wave(amplitude=200000, periods=60, dt=1e-4)
    if verbose:    
        print('Generating current signal...')    
    _, Current = generate_sine_wave(amplitude=30, offset=2, periods=60, dt=1e-4)

    NOW = datetime.now()
    
    if verbose:
        print('Generating DataFrame...')        
    df = pd.DataFrame(data={
        # Two AC signals
        'AC_Voltage': Voltage,
        'AC_Current': Current,
        
        # Example of a DC circuit ramping-up a voltage signal from 0 to 50,000
        # With a fixed current of ~10
        'DC_Voltage': map(lambda x: 50000 * (x/len(Voltage)), range(len(Voltage))),
        'DC_Current': map(lambda x: 10 - random.random(), range(len(Voltage))),                
        'Time': list(map(lambda x: NOW + timedelta(seconds=x), time)),
    })
    if verbose:
        print('Writing CSV...')            
    df.to_csv('data.csv')
    if verbose:
        print('Done, wrote Dataframe!')
        print(df)

if __name__ == '__main__':
    write_csv(True)

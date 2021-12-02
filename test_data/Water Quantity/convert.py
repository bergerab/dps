import os
from pathlib import Path
import pandas as pd
import glob

# this script requires that pandas and openpyxl is installed
# install using:
#     pip install pandas
#     pip install openpyxl
# script assumes files for each test have been placed in separate folders

start_path = os.path.abspath('.')
for wd in [os.path.join(start_path, 'Test' + str(i + 1)) for i in range(17)]:
    os.chdir(wd)
    # Process the electrical file
    cols = ['TIME', 'Vab', 'Vbc', 'Vca', 'Va', 'Vb', 'Vc', 'Ic', 'Ia', 'Ib', 'P (W)']
    nrows = 10000 # two seconds of 5khz data
    file_name = glob.glob('elec*.xlsx')[0]
    df = pd.read_excel(file_name, engine='openpyxl')
    df = df[cols].head(nrows).rename(columns={ 'TIME': 'Time' })
    df['Time'] = [x/(nrows/2) for x in range(0, nrows)]
    df.to_csv(Path(file_name).with_suffix('.csv'), index=False)
    os.remove(file_name) # delete the original file
    
    # Process the flow file
    file_name = glob.glob('flow*.csv')[0]
    cols = ['Time (YY:MM:DD hh:mm:ss.s)', 'Flow (US GPM)', 'Flow Velocity (FPS)']
    df = pd.read_csv(file_name)
    df = df[cols].rename(columns={ 'Time (YY:MM:DD hh:mm:ss.s)': 'Time' })
    nrows = len(df) // 10hz data -- just need two seconds of it
    df = df.head(20) # take two seconds
    df['Time'] = [x/10 for x in range(0, nrows)]
    df.to_csv(file_name, index=False)
    
    # Process the pressure file 
    file_name = glob.glob('press*.csv')[0]
    df = pd.read_csv(file_name) # 2hz data -- need two seconds
    df = df.head(4)
    cols = ['Time', 'pH_c', 'Coductivity_c', 'Free_Chlorine', 'Turbidity_C', 'Temp', 'TOC', 'DOC', 'UC254', 'pH', 'Conductivity', 'Turbidity', 'DX-Flow', 'DP1', 'DP2', 'FlowMeter']
    df = df[cols]
    nrows = len(df)
    df['Time'] = [x/2 for x in range(0, nrows)]
    df.to_csv(file_name, index=False)
    
    
    

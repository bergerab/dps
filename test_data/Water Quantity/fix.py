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
    nrows = 10000
    file_name = glob.glob('elec*.csv')[0]
    df = pd.read_csv(file_name)
    df['Time'] = [x/(nrows/2) for x in range(0, nrows)]
    df.to_csv(Path(file_name).with_suffix('.csv'), index=False)
    
    # Process the flow file
    file_name = glob.glob('flow*.csv')[0]
    df = pd.read_csv(file_name)
    df = df.head(20)
    df.to_csv(file_name, index=False)
    
    # Process the pressure file 
    file_name = glob.glob('press*.csv')[0]
    df = pd.read_csv(file_name)
    df = df.head(4)
    df.to_csv(file_name, index=False)
        
        
        
    

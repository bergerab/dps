import pandas as pd

# dplib contains all our code for computing KPIs.
import dplib

if __name__ == '__main__':
    print('Reading data.csv...')
    df = pd.read_csv('data.csv', parse_dates=['Time'])
    print('Running batch process...')
    
    # Compute desired KPIs, and return the KPIs in a new DataFrame object    
    result = dplib.ExampleSystem() \
        .run(df,
             # Specify which KPIs you want to compute (out of the ones the component supports):
             kpi_names=[
                 'Power',
                 'Load (Percent)',
                 'THD Voltage (Percent)',
                 'THD2 Voltage (Percent)',
                 'THD Voltage (Percent) at 50% Load'
             ],
             # Specify signal mappings and parameter values (constants)
             mapping={
                 # Signal Mappings
                 'Vdc': 'DC_Voltage',
                 'Idc': 'DC_Current',
                 'Va': 'AC_Voltage',
                
                 # Parameters
                 'MaxPower': 50000 * 10,
                 'VoltageBaseHarmonic': 60,
                 'SamplingFrequency': 1000,
             })
    kpi_df = result.df
    print('Batch process complete!')
    print('Writing to kpis.csv...')
    kpi_df.to_csv('kpis.csv')
    print('Done!')
    print(kpi_df)

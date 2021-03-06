import pandas as pd

# dplib contains all our code for computing KPIs.
import dplib as dp

if __name__ == '__main__':
    print('Reading data.csv...')
    df = pd.read_csv('data.csv', parse_dates=['Time'], index_col='Time')
    print('Running batch process...')
    print(df)
    
    # Compute desired KPIs, and return the KPIs in a new DataFrame object    
    result = dp.ExampleSystem() \
        .run(df,
             # Specify which KPIs you want to compute (out of the ones the component supports):
             kpi_names=[
                 'Power',
                 'Load (Percent)',
                 'THD Voltage (Percent)',
                 'THD2 Voltage (Percent)',
                 'THD Distorted Voltage (Percent)',
                 'THD2 Distorted Voltage (Percent)',
             ],
             # Specify signal mappings and parameter values (constants)
             mapping={
                 # Signal Mappings
                 'Vdc': 'DC_Voltage',
                 'Idc': 'DC_Current',
                 'Va': 'AC_Voltage',
                 'DistortedVa': 'Distorted AC_Voltage',                 
                
                 # Parameters
                 'MaxPower': 200 * 10,
                 'VoltageBaseHarmonic': 30,
                 'SamplingFrequency': 5000,
             })
    kpi_df = result.get_dataframe()
    print(kpi_df.index)
    print('Batch process complete!')
    print('Writing to kpis.csv...')
    kpi_df.to_csv('kpis.csv')
    print('Done!')
    print(kpi_df)

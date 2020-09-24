import pandas as pd

# dplib contains all our code for computing KPIs. It is installed via the dps_services package
import dplib as dp

# You can store KPIs as variables if you want to re-use them.
POWER = dp.KPI('DC_Voltage * DC_Current')
THD = dp.KPI('thd(window(Signal, "1s"), Freq) * 100')
AT_50_LOAD = dp.KPI('Signal if Load > 40 and Load < 60 else 0')
LOAD = dp.KPI('(CurrentValue / MaxValue) * 100')

# This MAX_DC_POWER is determined by gen.py (max voltage times max current).
MAX_DC_POWER = 50000 * 10

# Creating a BatchProcess specifies a set of KPIs to compute
# You must create one (as seen below), and then run it with "bp.run(df)" (see __main__).
#
# For the first KPI (the first call to .add(...) below), 
# We multiply DC_Voltage and DC_Current from the input file, and specify that the result is saved as "DC_Power" (in the output DataFrame)
# If the names in the KPI match exactly the names in the input DataFrame (e.g. "DC_Voltage" in the "DC_Power" KPI matches the name "DC_Voltage" in the input DataFrame), you don't need to specify a mapping dictionary. As a contrast, the rest of the KPIs below have mapping dictionaries.           
bp = dp.BatchProcess() \
       .add('DC_Power', POWER) \
       .add('Load %', LOAD, { # This dictionary is the "mapping dictionary" it is for mapping the name used in the KPI code (on the left), to the column name in the input DataFrame (on the right).
           'CurrentValue': 'DC_Power', # This maps "CurrentValue" from the KPI to the "DC_Power" column of the input data.
           'MaxValue': MAX_DC_POWER,
       }) \
       .add('THD % (AC_Voltage)', THD, {
           'Signal': 'AC_Voltage', # This maps the name "Signal" from the KPI to the "AC_Voltage" column of the input data.
           'Freq': 60, # The base harmonic for the signal
       }) \
       .add('THD % (AC_Current)', THD, {
           'Signal': 'AC_Current',
           'Freq': 60,
       }) \
       .add('THD % (AC_Current) at 50% Load', AT_50_LOAD, {
           'Signal': 'THD % (AC_Current)', # This maps the result of the "THD % (AC_Current)" to the AT_50_LOAD KPI's "Signal" name.
           'Load': 'Load %', # This maps the result of the "Load %" KPI (the second 
       })

if __name__ == '__main__':
    print('Reading data.csv...')
    df = pd.read_csv('data.csv', parse_dates=['Time'])
    print('Running batch process...')    
    kpi_df = bp.run(df) # Run the BatchProcess, and return the KPIs in a new DataFrame object
    print('Batch process complete!')
    print('Writing to kpis.csv...')
    kpi_df.to_csv('kpis.csv')
    print('Done!')
    print(kpi_df)


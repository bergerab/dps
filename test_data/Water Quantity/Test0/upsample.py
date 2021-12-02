import pandas as pd

eldf = pd.read_csv('elec_1750_1.csv')
fldf = pd.read_csv('flow_1750_1.csv')
prdf = pd.read_csv('press_1750_1.csv')

df = pd.DataFrame()

ei = 0
row_count = 0
for time in eldf['Time']:
    stay = True
    if ei+1 < len(fldf):
        val = fldf['Time'][ei+1]
        stay = time <= val
        
    if stay:
        row = fldf.iloc[ei].copy()
        row['Time'] = time
        df = df.append(row)
    else:
        ei += 1
        val = fldf['Time'][ei]
        row = fldf.iloc[ei].copy()
        row['Time'] = time
        df = df.append(row)
    row_count += 1

print(df)

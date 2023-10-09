import pandas as pd
import csv

#load data
df = pd.read_csv('AIS_2023_01_01.csv')

# Take the first MMSI
first = df.groupby('MMSI').apply(lambda t: t.iloc[0])

# Print all rows that have the same MMSI as the first row
print(df[df['MMSI'] == first.iloc[0]['MMSI']])
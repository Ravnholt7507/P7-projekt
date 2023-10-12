import pandas as pd
pd.set_option('display.max_columns', 20)

n = 150000

df = pd.read_csv('AIS_2023_01_01.csv', nrows=n)
df = df.sort_values(["MMSI","BaseDateTime"])

#Take ships where the SOG is greater than 5
df = df.drop(df[df.SOG < 5].index)

# Take MMSI where there are more than 10 rows
df = df.groupby(['MMSI']).filter(lambda x: len(x) > 10)

#Take row where MMSI is 209941000
# df = df.loc[df['MMSI'] == 209941000]

df.to_csv('boats.csv', index=False)
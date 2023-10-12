import pandas as pd
pd.set_option('display.max_columns', 20)

n = 150000

df = pd.read_csv('AIS_2023_01_01.csv', nrows=n)
df = df.sort_values(["MMSI","BaseDateTime"])

df = df.groupby(['MMSI']).filter(lambda x: len(x) > 24)

df.to_csv('boats.csv', index=False)
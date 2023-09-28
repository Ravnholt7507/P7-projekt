import pandas as pd
pd.set_option('display.max_columns', 20)
n = 10000

chunks = pd.read_csv('AIS_2023_01_01_1.csv', chunksize=n)
df = next(chunks)

df.to_csv('boats.csv', sep=',')
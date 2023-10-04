import pandas as pd
pd.set_option('display.max_columns', 20)

n = 150000

df = pd.read_csv('AIS_2023_01_01.csv', nrows=n)
df = df.sort_values(["MMSI","BaseDateTime"])

<<<<<<< Updated upstream
# df = df.groupby(['MMSI']).filter(lambda x: len(x) > 24)
df = df[df['MMSI'] == 224989000]
=======
df = df.groupby(['MMSI']).filter(lambda x: len(x) > 24)
>>>>>>> Stashed changes

df.to_csv('boats.csv', index=False)
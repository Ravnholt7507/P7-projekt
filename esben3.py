import random
import numpy as np
import pandas as pd

Limit = 50000

RNRN = random.sample(range(1, Limit-1), 10000)
print(np.sort(RNRN))
print(len(np.unique(RNRN)))

df = pd.read_csv('data/AIS_2023_01_01.csv', nrows=Limit)

for x in range(len(RNRN)):
    df.iloc[RNRN[x], df.columns.get_loc('COG')] = None

df.to_csv('data/skovl.csv')
import pandas as pd
import time
from haversine import haversine
from tqdm import tqdm

start_time = time.time()
#df = pd.read_csv('../data/filtered.csv')
df = pd.read_csv('../data/AIS_2023_01_01.csv', nrows=500000)
df = df.drop(columns=['VesselName', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])
print(len(df))

tally = 0
count = 0
totalruns = 0

for mmsi, group in tqdm(df.groupby('MMSI'), desc='8=====>'):
    group = group.reset_index(drop=True)
    totalruns += 1
    for i in range(len(group) - 1):
        actual = df.iloc[i]['LAT'], df.iloc[i]['LON'] 
        for j in range(i+1, len(group) - 1):
            predicted = df.iloc[j]['LAT'], df.iloc[j]['LON']
            dist = haversine(actual,predicted)
            if dist  > 0.05:
                i =  j
                tally += dist
                count += 1
                break

print('tally', tally)
print('count', count)
print('8========>', totalruns)
print('avg distance: ', tally / count)
print('time', time.time() - start_time, 'seconds')




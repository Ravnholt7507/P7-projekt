import pandas as pd
import time
from haversine import haversine
from tqdm import tqdm

start_time = time.time()
df = pd.read_csv('../data/filtered_limited.csv')
# df = pd.read_csv('../data/AIS_2023_01_01.csv', nrows=500000)
df = df.drop(columns=['VesselName', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])
print(len(df))

total_distance = 0
count = 0
totalruns = 0

for mmsi, group in tqdm(df.groupby('MMSI'), desc='MMSI'):
    group = group.reset_index(drop=True)
    totalruns += 1
    for i in range(len(group) - 1):
        actual = df.iloc[i]['LAT'], df.iloc[i]['LON'] 
        for j in range(i+1, len(group) - 1):
            predicted = df.iloc[j]['LAT'], df.iloc[j]['LON']
            dist = haversine(actual,predicted)
            if dist  > 0.05:
                i =  j
                total_distance += dist
                count += 1


avg_distance = total_distance / count 
elapsed_time = time.time() - start_time

print('point based test')
print(f'Total distance: {total_distance} kilometers')
print(f'Number of measurements: {count}')
print(f'Total runs: {totalruns}')
print(f'Average distance: {avg_distance} kilometers')
print(f'Elapsed time: {elapsed_time} seconds')
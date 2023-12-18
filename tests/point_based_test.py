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

total_distance = 0
count = 0
count2 = 0
total_count = 0
totalruns = 0
still_distance = 0
threshold_dist = 0
df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])

for mmsi, group in tqdm(df.groupby('MMSI'), desc='MMSI'):
    group = group.reset_index(drop=True)
    totalruns += 1
    i = 0
    while i < len(group) - 1:
        actual = group.iloc[i]['LAT'], group.iloc[i]['LON']
        j = i + 1
        while j < len(group) - 1:
            predicted = group.iloc[j]['LAT'], group.iloc[j]['LON']
            dist = haversine(actual,predicted)
            total_distance += dist
            total_count += 1
            if dist  > 0.05:
                threshold_dist += dist
                count += 1
                i = j
                break
            else:
                count2 += 1
                still_distance += dist
                j += 1
        else:
            i += 1

elapsed_time = time.time() - start_time

# drop last row of each group
df = df.groupby('MMSI').apply(lambda group: group.iloc[:-1]).reset_index(drop=True)

print('point based test')
print(f'Total boats: {len(df)}')
print(f'Number of measurements: {count}')
print(f'Number of still measurements: {count2}')
print(f'MMSI`s: {totalruns}')

print(f'Avg total distance: {total_distance / total_count} kilometers')

if count != 0:
    print(f'Threshold distance: {threshold_dist} kilometers')
    threshold_dist = threshold_dist / count
    print(f'Average threshold distance: {threshold_dist * 1000} meters') 
if count2 != 0:
    print(f'Still distance: {still_distance} kilometers')
    avg_still_distance = still_distance / count2
    print(f'Average still distance: {avg_still_distance * 1000} meters')
    
print(f'Elapsed time: {elapsed_time} seconds')
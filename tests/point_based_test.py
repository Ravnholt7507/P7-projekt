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
totalruns = 0
still_distance = 0
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

            if dist  > 0.05:
                total_distance += dist
                count += 1
                i = j
                break
            else:
                count2 += 1
                still_distance += dist
                j += 1
        else:
            i += 1

avg_distance = total_distance / count
elapsed_time = time.time() - start_time

avg_still_distance = still_distance / count2

total_distance = total_distance + still_distance


# drop last row of each group
df = df.groupby('MMSI').apply(lambda group: group.iloc[:-1]).reset_index(drop=True)

print('point based test')
print(f'Total boats: {len(df)}')
print(f'Number of measurements: {count}')
print(f'Number of still measurements: {count2}')
print(f'Total runs: {totalruns}')
print(f'Total distance: {total_distance} kilometers')
print(f'Average distance: {avg_distance} kilometers')
print(f'Average still distance: {avg_still_distance * 1000}  meters')
print(f'Elapsed time: {elapsed_time} seconds')

# print('mmsi', mmsi)
# print('i', i, 'j', j, 'dist', dist)

# # print time diff
# print('time diff', group.iloc[j]['BaseDateTime'] - group.iloc[i]['BaseDateTime'])
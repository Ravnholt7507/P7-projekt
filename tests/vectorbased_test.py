import pandas as pd
import time
from haversine import haversine
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic

# Vectorbased test

start_time = time.time()
df = pd.read_csv('../data/filtered_limited.csv')
df = df.drop(columns=['VesselName','Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 2)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])

count = 0
total_distance = 0

for mmsi, group in df.groupby('MMSI'):
    group = group.reset_index(drop=True)
    for i in range(len(group) - 2):

        COGresult = Geodesic.WGS84.Inverse(group.loc[i, 'LAT'], group.loc[i, 'LON'], group.loc[i+1, 'LAT'], group.loc[i+1, 'LON'])
        traveled = (group.loc[i, 'SOG']* 1.852) * ((pd.to_datetime(group.loc[i+2, 'BaseDateTime']) - pd.to_datetime(group.loc[i+1, 'BaseDateTime'])).total_seconds() / 3600)

        time_diff = (pd.to_datetime(group.loc[i+2, 'BaseDateTime']) - pd.to_datetime(group.loc[i+1, 'BaseDateTime'])).total_seconds()
        df.loc[i+1, 'time_diff'] = time_diff
        # Save traveled to df
        df.loc[i+1, 'traveled'] = traveled
        
        prediction = geodesic(kilometers=traveled).destination((group.loc[i+1, 'LAT'], group.loc[i+1, 'LON']), COGresult['azi1'])
        act = (group.loc[i+2, 'LAT'], group.loc[i+2, 'LON'])
        pred = ([prediction.latitude, prediction.longitude])

        distance = haversine(act,pred)

        total_distance += distance
        count += 1


# Drop the first row of each group
df = df.groupby('MMSI').apply(lambda group: group.iloc[1:]).reset_index(drop=True)
# Print results
total_boats = len(df)

unique_boats = len(df['MMSI'].unique())
avg_distance = (total_distance / count) * 1000  # Converting kilometers to meters
elapsed_time = time.time() - start_time

print('Vector based test')
print(f'Total boats: {total_boats}')
print(f'Unique boats: {unique_boats}')
print(f'Total distance: {total_distance} km')
print(f'Average distance: {avg_distance} meters')
print(f'Elapsed time: {elapsed_time} seconds')

df.to_csv('../data/test2.csv', index=False)
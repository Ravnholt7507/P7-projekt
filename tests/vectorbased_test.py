import pandas as pd
import time
from haversine import haversine
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic

# Vectorbased test

start_time = time.time()
df = pd.read_csv('../data/filtered.csv')
df = df.drop(columns=['VesselName','Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 2)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])

count = 0
tally = 0

for mmsi, group in df.groupby('MMSI'):
    group = group.reset_index(drop=True)
    for i in range(len(group) - 2):

        COGresult = Geodesic.WGS84.Inverse(group.loc[i, 'LAT'], group.loc[i, 'LON'], group.loc[i+1, 'LAT'], group.loc[i+1, 'LON'])
        traveled = (group.loc[i, 'SOG']* 1.852) * ((pd.to_datetime(group.loc[i+2, 'BaseDateTime']) - pd.to_datetime(group.loc[i+1, 'BaseDateTime'])).total_seconds() / 3600)

        time_diff = (pd.to_datetime(group.loc[i+2, 'BaseDateTime']) - pd.to_datetime(group.loc[i+1, 'BaseDateTime'])).total_seconds()
        df.loc[i+1, 'time_diff'] = time_diff
        # Save traveled to df
        df.loc[i+1, 'traveled'] = traveled
        print('time1', group.loc[i+1, 'BaseDateTime'])
        print('time2', group.loc[i+2, 'BaseDateTime'])
        print('time_diff', time_diff)
        print('----')
        
        
        prediction = geodesic(kilometers=traveled).destination((group.loc[i+1, 'LAT'], group.loc[i+1, 'LON']), COGresult['azi1'])
        act = (group.loc[i+2, 'LAT'], group.loc[i+2, 'LON'])
        pred = ([prediction.latitude, prediction.longitude])

        distance = haversine(act,pred)

        tally += distance
        count += 1
    break

# Print results
print('boats', len(df))
print(len(df['MMSI'].unique()))
print('total', tally)
print('count', count)
print('avg distance: ', (tally / count) * 1000, 'meters')
print('time', time.time() - start_time, 'seconds')
df.to_csv('../data/test2.csv', index=False)
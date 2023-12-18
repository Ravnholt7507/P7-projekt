import pandas as pd
import time
from haversine import haversine
from geopy.distance import geodesic

start_time = time.time()
df = pd.read_csv('../data/filtered_unlimited.csv')
df = df.drop(columns=['VesselName','Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])

# Convert BaseDateTime to datetime format
df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])

# Calculate time difference in seconds
df['time_diff'] = df.groupby('MMSI')['BaseDateTime'].diff().dt.total_seconds()

#remove the first element from timediff
df['time_diff'] = df['time_diff'].shift(-1)

# Calculate traveled distance
df['traveled'] = df['SOG'] * 1.852 * df['time_diff'] / 3600

# Drop rows where 'traveled' is NaN
df['traveled'] = df['traveled'].fillna(0)

# Calculate prediction
df['prediction'] = df.apply(lambda row: geodesic(kilometers=row['traveled']).destination((row['LAT'], row['LON']), row['COG']), axis=1)

# Calculate actual position
df['act'] = list(zip(df['LAT'].shift(-1), df['LON'].shift(-1)))

# Calculate predicted position
df['pred'] = df['prediction'].apply(lambda x: [x.latitude, x.longitude])

# Calculate haversine distance
df['distance'] = df.apply(lambda row: haversine(row['act'], row['pred']), axis=1)

# Drop the last row of each group
df = df.groupby('MMSI').apply(lambda group: group.iloc[:-1]).reset_index(drop=True)

df = df.drop(columns=['traveled', 'prediction', 'act', 'pred'])

# Print results
print('boats', len(df))
print(len(df['MMSI'].unique()))
print('total', df['distance'].sum())
print('count', df['distance'].count())
print('avg distance: ', (df['distance'].mean()) * 1000, 'meters')
print('time', time.time() - start_time, 'seconds')
import pandas as pd
from haversine import haversine_vector, Unit
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
from geopy.point import Point
import numpy as np

# Vectorbased test
df = pd.read_csv('../data/filtered.csv')
df = df.drop(columns=['VesselName','Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 2)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])


df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
df['time_diff'] = df.groupby('MMSI')['BaseDateTime'].diff().dt.total_seconds().div(3600)  # in hours
df['time_diff2'] = df.groupby('MMSI')['BaseDateTime'].diff().dt.total_seconds()  # in seconds
# Shift time_diff to the next row
df['time_diff'] = df['time_diff'].shift(-1)
df['time_diff2'] = df['time_diff2'].shift(-1)

df['Traveled'] = df['SOG'].shift(-1) * 1.852 * df['time_diff']  # in km

df['Next_LAT'] = df['LAT'].shift(-1)
df['Next_LON'] = df['LON'].shift(-1)

# Calculate the initial bearing (COG) between current point and next point
cog = []
for i in range(len(df) - 1):
    cog.append(Geodesic.WGS84.Inverse(df.iloc[i]['LAT'], df.iloc[i]['LON'], df.iloc[i+1]['Next_LAT'], df.iloc[i+1]['Next_LON'])['azi1'])
cog.append(np.nan)  # for the last row
df['COG'] = cog

# Drop rows with NaN values in 'LAT', 'LON', 'Traveled', or 'COG'
df = df.dropna(subset=['LAT', 'LON', 'Traveled', 'COG'])
# Calculate the predicted next point
df['Prediction_LAT'], df['Prediction_LON'], _ = zip(*df.apply(lambda row: geodesic(kilometers=row['Traveled']).destination((row['LAT'], row['LON']), row['COG']), axis=1))

# Calculate the actual next point
df['Act_LAT'] = df['LAT'].shift(-2)
df['Act_LON'] = df['LON'].shift(-2)
# Convert 'Act' and 'Pred' into arrays of shape (n, 2)
act = df[['Act_LAT', 'Act_LON']].values
pred = df[['Prediction_LAT', 'Prediction_LON']].values

# Calculate the distance between the predicted next point and the actual next point
df['Distance'] = haversine_vector(act, pred, Unit.KILOMETERS)
# drop columns
df = df.drop(columns=['Next_LAT', 'Next_LON', 'Prediction_LAT', 'Prediction_LON', 'Act_LAT', 'Act_LON','time_diff', 'Traveled'])


# Print results
print('boats', len(df))
print(len(df['MMSI'].unique()))
print('total', df['Distance'].sum())
print('count', df['Distance'].count())
print('avg distance: ', df['Distance'].mean() * 1000, 'meters')

df.to_csv('../data/test2.2.csv', index=False)
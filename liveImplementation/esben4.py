from geopy.distance import distance
import pandas as pd
import numpy as np
from haversine import haversine

timeIntervals = 10

df = pd.read_csv('../data/filtered.csv')
df = df.drop(columns=['VesselName','Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
df = df.sort_values(by=['MMSI', 'BaseDateTime'])
print(df)

tally = 0

for mmsi in df['MMSI'].unique():
    df[df['MMSI'] == mmsi]

    traveled = (df.iloc[0]['SOG']* 1.852) * ((pd.to_datetime(df.iloc[1]['BaseDateTime']) - pd.to_datetime(df.iloc[0]['BaseDateTime'])).total_seconds() / 3600)
    print(traveled)

    prediction = distance(kilometers=traveled).destination((df.iloc[0]['LAT'], df.iloc[0]['LON']), df.iloc[0]['COG'])

    skovl = (df.iloc[1]['LAT'], df.iloc[1]['LON'])
    skovl2 = ([prediction[0], prediction[1]])

    distance = haversine(skovl,skovl2)

    tally += distance

#print(tally / len(df['MMSI'].unique()))

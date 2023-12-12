import pandas as pd
from geopy.distance import geodesic

df = pd.read_csv("../data/AIS_2023_01_01.csv", nrows=50000)
df = df[(df['LAT'] > 23) & (df['LAT'] < 24) & (df['LON'] > -82) & (df['LON'] < -80)]
df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)


# Data is on the form:
# MMSI, BaseDateTime, LAT, LON, SOG, COG, Heading, VesselName, IMO, CallSign, VesselType, Status, Length, Width, Draft, Cargo, TransceiverClass
# Calculate distance between two points of each row per mmsi
for mmsi in df['MMSI'].unique():
    ship = df[df['MMSI'] == mmsi]
    length = len(ship)
    for i in range(length - 1):
        lat1 = ship.iloc[i]['LAT']
        lon1 = ship.iloc[i]['LON']
        lat2 = ship.iloc[i + 1]['LAT']
        lon2 = ship.iloc[i + 1]['LON']
        dis = geodesic((lat1, lon1), (lat2, lon2)).km
        df.loc[ship.index[i], 'distance'] = dis
    
# Calculate time between two points of each row per mmsi
for mmsi in df['MMSI'].unique():
    ship = df[df['MMSI'] == mmsi]
    length = len(ship)
    for i in range(length - 1):
        time1 = ship.iloc[i]['BaseDateTime']
        time2 = ship.iloc[i + 1]['BaseDateTime']
        time_diff = (pd.to_datetime(time2) - pd.to_datetime(time1)).total_seconds()
        df.loc[ship.index[i], 'time'] = time_diff

# Calculate speed between two points of each row per mmsi
for mmsi in df['MMSI'].unique():
    ship = df[df['MMSI'] == mmsi]
    length = len(ship)
    for i in range(length - 1):
        dis = ship.iloc[i]['distance']
        time = ship.iloc[i]['time']
        speed = dis / time
        df.loc[ship.index[i], 'speed'] = speed

# Drop MMSI where speed is not 0 (ship is not stationary) and SOG is 0 (ship is not moving)

# Calculate difference between SOG and speed
df['diff'] = df['SOG'] - df['speed']

# Drop MMSI where distance is above 1 and time is below 10
df = df.drop(df[(df['distance'] > 5) & (df['time'] < 5)].index)

# Drop MMSI where distance is above 1 and SOG is below 1
df = df.drop(df[(df['distance'] > 5) & (df['SOG'] < 0.3)].index)

# Drop MMSI where distance == 0
df = df.drop(df[df['distance'] == 0].index)

# Drop MMSI 

# Drop whole MMSI where sog == 102.3
df = df.drop(df[df['SOG'] == 102.3].index)

# Drop whole MMSI where abs diff > 10
df = df.drop(df[abs(df['diff']) > 10].index)

# remove distance,time,speed,diff
# df = df.drop(columns=['distance', 'time', 'speed', 'diff'])

df.to_csv('../data/filtered.csv', index=False)

# output_df = pd.read_csv('../data/output.csv')
# output_df.sort_values(by=['MMSI','SOG'], inplace=True, ascending=False)
# output_df.to_csv('../data/output.csv', index=False)
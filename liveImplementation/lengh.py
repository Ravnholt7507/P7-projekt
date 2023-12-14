import pandas as pd

df = pd.read_csv("../data/AIS_2023_01_01.csv")
# sort = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)
# sort = sort.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign',
#               'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo'])
# sort.to_csv('../data/sorted.csv', index=False)

print("length of df: ", len(df))
init = len(df)

limit = True
if limit:
    df = df[(df['LAT'] > 23) & (df['LAT'] < 24) & (df['LON'] > -82) & (df['LON'] < -80)]
    print('Area is limited between 23 and 24 lat and -82 and -80 lon')

# Drop rows where heading == 511.0
df = df[df['Heading'] != 511.0]
df = df.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign',
              'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo','TransceiverClass'])

# Drop whole MMSI where sog == 102.3
df = df[df['SOG'] != 102.3]

df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)

# Calculate time between two points of each row per mmsi
df['BaseDateTime_shifted'] = df.groupby('MMSI')['BaseDateTime'].shift()
# Time in hours
df['time'] = (pd.to_datetime(df['BaseDateTime']) - pd.to_datetime(df['BaseDateTime_shifted'])).dt.total_seconds() / 3600
df = df.drop(columns=['BaseDateTime_shifted'])

# remove duplicates
from math import radians, sin, cos, sqrt, atan2

# Define a function to calculate distance between two points
def calculate_distance(lat1, lon1, lat2, lon2):
  # approximate radius of earth in km
  R = 6371.0

  lat1_rad = radians(lat1)
  lon1_rad = radians(lon1)
  lat2_rad = radians(lat2)
  lon2_rad = radians(lon2)

  dlon = lon2_rad - lon1_rad
  dlat = lat2_rad - lat1_rad

  a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))

  distance = R * c
  return distance

# Calculate change in latitude and longitude for each row per MMSI
df['LAT_change'] = df.groupby('MMSI')['LAT'].diff()
df['LON_change'] = df.groupby('MMSI')['LON'].diff()

# Calculate distance for each row
# Distance in km
df['distance'] = df.apply(lambda row: calculate_distance(row['LAT'], row['LON'], row['LAT'] + row['LAT_change'], row['LON'] + row['LON_change']), axis=1)

# Calculate speed
df['speed'] = (df['distance'] / df['time']) / 1.852

# Calculate difference between SOG and speed
df['diff'] = df['SOG'] - df['speed']

# Drop rows based on conditions
# 0.014 degrees per second corresponds to ~50 knots
# Drop rows where latitude change is greater than 0.014 degrees per second and time is less than 5 seconds
# Identify MMSI values that have any failing records
failing_mmsi = df[(df['LAT_change'].abs() > 0.014) & (df['time'] < 30/3600) |
                  (df['LON_change'].abs() > 0.014) & (df['time'] < 30/3600) |
                  # (df['LAT_change'].abs() > 0.014) & (df['SOG'] < 0.3) |
                  # (df['LON_change'].abs() > 0.014) & (df['SOG'] < 0.3) |
                  # (df['LAT_change'] == 0) & (df['LON_change'] == 0) |
                  (df['diff'].abs() > 2)]['MMSI'].unique()


# test = df[(df['LAT_change'].abs() > 0.014) & (df['time'] < 30/3600)]
# test2 = df[(df['LON_change'].abs() > 0.014) & (df['time'] < 30/3600)]
# test.to_csv('../data2/testlat.csv', index=False)
# test2.to_csv('../data2/testlon.csv', index=False)
# test3 = df[(df['LAT_change'].abs() > 0.014) & (df['SOG'] < 0.3)]
# test4 = df[(df['LON_change'].abs() > 0.014) & (df['SOG'] < 0.3)]
# test3.to_csv('../data2/testlat2.csv', index=False)
# test4.to_csv('../data2/testlon2.csv', index=False)
# test6 = df[(df['diff'].abs() > 2)]
# # Calculate time to seconds
# test6['time'] = test6['time'] * 3600
# test6.to_csv('../data2/testdiff.csv', index=False)


# print 0.014 degrees to meters
# 1 degree = 111 km
# 0.014 * 111000 = 1554 meters

# How long does it take to travel 1554 meters at 50 knots?
# 1554 / 50 = 31.08 seconds

# Make new condition for time
# Drop rows where latitude change is greater than 0.014 degrees per second and time

# Drop all records with failing MMSI values
df = df[~df['MMSI'].isin(failing_mmsi)]
# remove extra columns
df = df.drop(columns=['LAT_change','LON_change','speed', 'diff'])
after = len(df)
print("length of df: ", len(df))
print('rows dropped: ', (init - after) / init * 100, '%')
df.to_csv('../data/filtered.csv', index=False)
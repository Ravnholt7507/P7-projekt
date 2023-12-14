import pandas as pd

df = pd.read_csv("../data/AIS_2023_01_01.csv")
print("length of df: ", len(df))
init = len(df)

limit = True
if limit:
    df = df[(df['LAT'] > 23) & (df['LAT'] < 24) & (df['LON'] > -82) & (df['LON'] < -80)]
    print('Area is limited between 23 and 24 lat and -82 and -80 lon')

# Drop rows where heading == 511.0
df = df[df['Heading'] != 511.0]

# Drop whole MMSI where sog == 102.3
df = df[df['SOG'] != 102.3]

df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)

# remove duplicates
df = df.drop_duplicates(subset=['MMSI', 'BaseDateTime'], keep='first')

# Calculate change in latitude and longitude for each row per MMSI
df['LAT_change'] = df.groupby('MMSI')['LAT'].diff()
df['LON_change'] = df.groupby('MMSI')['LON'].diff()

# Calculate time between two points of each row per mmsi
df['BaseDateTime_shifted'] = df.groupby('MMSI')['BaseDateTime'].shift()
df['time'] = (pd.to_datetime(df['BaseDateTime']) - pd.to_datetime(df['BaseDateTime_shifted'])).dt.total_seconds()

# Calculate speed between two points of each row per mmsi
df['speed'] = df['LAT_change'] / df['time']

# Calculate difference between SOG and speed
df['diff'] = df['SOG'] - df['speed']

# Drop rows based on conditions
# 0.014 degrees per second corresponds to ~50 knots
# Drop rows where latitude change is greater than 0.014 degrees per second and time is less than 5 seconds
# Identify MMSI values that have any failing records
failing_mmsi = df[(df['LAT_change'].abs() > 0.014) & (df['time'] < 5) |
                  (df['LON_change'].abs() > 0.014) & (df['time'] < 5) |
                  (df['LAT_change'].abs() > 0.014) & (df['SOG'] < 0.3) |
                  (df['LON_change'].abs() > 0.014) & (df['SOG'] < 0.3) |
                #   (df['LAT_change'] == 0) & (df['LON_change'] == 0) |
                  (df['diff'].abs() > 10)]['MMSI'].unique()

# Drop all records with failing MMSI values
df = df[~df['MMSI'].isin(failing_mmsi)]
# remove extra columns
df = df.drop(columns=['LAT_change', 'time','LON_change','Heading', 'BaseDateTime_shifted', 'speed', 'diff'])
after = len(df)
print("length of df: ", len(df))
print('rows dropped: ', (init - after) / init * 100, '%')
df.to_csv('../data/filtered.csv', index=False)
import pandas as pd
import DataHandler as dh

def filter():
  df = pd.read_csv("../data/AIS_2023_01_01.csv")

  print("length of AIS data: ", len(df))
  init = len(df)

  limit = True
  if limit:
    df = df[(df['LAT'] > 23) & (df['LAT'] < 24) & (df['LON'] > -82) & (df['LON'] < -80)]
    print('Area is limited between 23 and 24 lat and -82 and -80 lon')

  # Drop trash values
  df = df[df['Heading'] != 511.0]
  df = df[df['SOG'] != 102.3]

  df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)

  # Calculate time between two points of each row per mmsi
  df['BaseDateTime_shifted'] = df.groupby('MMSI')['BaseDateTime'].shift()

  # Time in hours
  df['time'] = (pd.to_datetime(df['BaseDateTime']) - pd.to_datetime(df['BaseDateTime_shifted'])).dt.total_seconds() / 3600
  df = df.drop(columns=['BaseDateTime_shifted'])

  # Calculate change in latitude and longitude for each row per MMSI
  df['LAT_change'] = df.groupby('MMSI')['LAT'].diff()
  df['LON_change'] = df.groupby('MMSI')['LON'].diff()

  # Calculate distance for each row
  # Distance in km
  df['distance'] = df.apply(lambda row: dh.calculate_distance(row['LAT'], row['LON'], row['LAT'] + row['LAT_change'], row['LON'] + row['LON_change']), axis=1)

  # Calculate speed in knots
  df['speed'] = (df['distance'] / df['time']) / 1.852

  # Calculate difference between SOG and speed
  df['diff'] = df['SOG'] - df['speed']

  # 0.014 degrees per second corresponds to ~50 knots
  # Drop rows where latitude change is greater than 0.014 degrees per second and time is less than 30 seconds
  # Identify MMSI values that have any failing records
  failing_mmsi = df[(df['LAT_change'].abs() > 0.014) & (df['time'] < 30/3600) |
                    (df['LON_change'].abs() > 0.014) & (df['time'] < 30/3600) |
                    (df['diff'].abs() > 2)]['MMSI'].unique()

  # Drop all records with failing MMSI values
  df = df[~df['MMSI'].isin(failing_mmsi)]
  # remove extra columns

  df = df.drop(columns=['LAT_change','LON_change','speed', 'diff', 'distance', 'time'])
  after = len(df)
  df = df.drop_duplicates(keep='first')

  print("length of df: ", len(df))
  print('rows dropped: ', (init - after) / init * 100, '%')

  if limit:
      print('saved to filtered_limited.csv')
      df.to_csv('../data/filtered_limited.csv', index=False)
  else:
    print('saved to filtered_unlimited.csv')
    df.to_csv('../data/filtered_unlimited.csv', index=False)

  return df
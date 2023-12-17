import pandas as pd
import DataHandler as dh
def load_data():
  df = pd.read_csv("../data/AIS_2023_01_01.csv")
  return df

def limit_area(df):
  df = df[(df['LAT'] > 23) & (df['LAT'] < 24) & (df['LON'] > -82) & (df['LON'] < -80)]
  print('Area is limited between 23 and 24 lat and -82 and -80 lon')
  return df

def drop_invalid_rows(df):
  #df = df[df['Heading'] != 511.0]
  df = df[df['SOG'] != 102.3]
  return df

def calculate_time(df):
  df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)
  df['BaseDateTime_shifted'] = df.groupby('MMSI')['BaseDateTime'].shift()
  df['time'] = (pd.to_datetime(df['BaseDateTime']) - pd.to_datetime(df['BaseDateTime_shifted'])).dt.total_seconds() / 3600
  df = df.drop(columns=['BaseDateTime_shifted'])
  return df

def calculate_distance(df):
  df['LAT_change'] = df.groupby('MMSI')['LAT'].diff()
  df['LON_change'] = df.groupby('MMSI')['LON'].diff()
  df['distance'] = df.apply(lambda row: dh.calculate_distance(row['LAT'], row['LON'], row['LAT'] + row['LAT_change'], row['LON'] + row['LON_change']), axis=1)
  return df

def calculate_speed(df):
  df['speed'] = (df['distance'] / df['time']) / 1.852
  return df

def calculate_difference(df):
  df['diff'] = df['SOG'] - df['speed']
  return df

def drop_invalid_records(df):
  failing_mmsi = df[(df['LAT_change'].abs() > 0.014) & (df['time'] < 30/3600) |
                    (df['LON_change'].abs() > 0.014) & (df['time'] < 30/3600) |
                    (df['diff'].abs() > 2)]['MMSI'].unique()
  df = df[~df['MMSI'].isin(failing_mmsi)]
  return df

def remove_extra_columns(df):
  df = df.drop(columns=['LAT_change','LON_change','speed', 'diff', 'distance', 'time'])
  return df

def save_filtered_data(df, limit):
  if limit:
      print('saved to filtered_limited.csv')
      df.to_csv('../data/filtered_limited.csv', index=False)
  else:
      print('saved to filtered_unlimited.csv')
      df.to_csv('../data/filtered_unlimited.csv', index=False)

def filter_data():
  df = load_data()
  print("length of AIS data: ", len(df))
  init = len(df)

  limit = True
  if limit:
      df = limit_area(df)

  df = drop_invalid_rows(df)
  df = calculate_time(df)
  df = calculate_distance(df)
  df = calculate_speed(df)
  df = calculate_difference(df)
  df = drop_invalid_records(df)
  df = remove_extra_columns(df)

  after = len(df)
  df = df.drop_duplicates(keep='first')

  print("length of df: ", len(df))
  print('rows dropped: ', (init - after) / init * 100, '%')

  save_filtered_data(df, limit)

  return df


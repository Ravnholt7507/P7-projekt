import pandas as pd

def cleanse(save_to):
     pd.set_option('display.max_columns', 20)

     n = 150000

     # df = pd.read_csv('data/AIS_2023_01_01.csv',nrows=n)
     df = pd.read_csv('data/AIS_2023_01_01.csv')

     df = df.sort_values(by=['MMSI', 'BaseDateTime'])

     df = df[df.SOG > 5]

     # Drop all rows where the ship speed is 102.3
     df = df[df.SOG != 102.3]

     # df = df[(df.LAT > 23) & (df.LAT < 24) & (df.LON > -82) & (df.LON < -80)]

     # Drop all MMSI where the time between its two rows is greater than 5 minutes
     df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
     df['BaseDateTime'] = df['BaseDateTime'].dt.tz_localize(None)
     df['BaseDateTime'] = df['BaseDateTime'].astype('datetime64[ns]')
     df['diff'] = df.groupby('MMSI')['BaseDateTime'].diff()
     df = df[df['diff'] < '00:05:00']
     
     #df = df.drop_duplicates(subset='MMSI', keep='First')

     # Drop all ships with less than 2 rows
     df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
     
     
     df = df.groupby('MMSI').tail(2)

     df.to_csv(save_to, index=False)
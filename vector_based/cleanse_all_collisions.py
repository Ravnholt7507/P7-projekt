import pandas as pd

def cleanse(save_to):
     
     df = pd.read_csv('data/AIS_2023_01_01.csv')
     df = df.sort_values(by=['MMSI', 'BaseDateTime'])
     df = df[df.SOG > 2]

     # Drop all ships with less than 2 rows
     df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
     
     # Tale the last two rows of each ship
     df = df.groupby('MMSI').tail(2)
     
     # Remove all MMSI where the last two rows are more than 5 minutes apart
     df = df.groupby('MMSI').filter(lambda x: pd.to_datetime(x['BaseDateTime'].iloc[1]) - pd.to_datetime(x['BaseDateTime'].iloc[0]) <= pd.Timedelta(minutes=5))
     
     df.to_csv(save_to, index=False)
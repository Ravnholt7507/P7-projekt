import pandas as pd

def cleanse(save_to):
     pd.set_option('display.max_columns', 20)

     n = 150000  # number of records in file
     # Read the CSV file
     df = pd.read_csv('data/AIS_2023_01_01.csv')

     # Sort the data by MMSI and BaseDateTime
     df = df.sort_values(by=['MMSI', 'BaseDateTime'])
     
     # Drop all ships where the SOG is less than 2
     df = df[df.SOG > 2]

     # Drop all ships with less than 2 rows
     df = df.groupby('MMSI').filter(lambda x: len(x) > 1)
     
     # Tale the last two rows of each ship
     df = df.groupby('MMSI').tail(2)
     
     # Remove all MMSI where the last two rows are more than 5 minutes apart
     df = df.groupby('MMSI').filter(lambda x: pd.to_datetime(x['BaseDateTime'].iloc[1]) - pd.to_datetime(x['BaseDateTime'].iloc[0]) <= pd.Timedelta(minutes=5))
     
     df.to_csv(save_to, index=False)
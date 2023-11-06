import pandas as pd

def cleanse(save_to):
     pd.set_option('display.max_columns', 20)

     n = 150000

     df = pd.read_csv('data/AIS_2023_01_01.csv')

     df = df.sort_values(by=['MMSI', 'BaseDateTime'])

     df = df[df.SOG > 5]

     # df = df[(df.LAT > 23) & (df.LAT < 24) & (df.LON > -82) & (df.LON < -80)]

     #df = df.drop_duplicates(subset='MMSI', keep='First')

     df = df.groupby('MMSI').tail(2)

     df.to_csv(save_to, index=False)
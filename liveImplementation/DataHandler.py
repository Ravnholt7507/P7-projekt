import pandas as pd
import numpy as np
from tqdm import tqdm
import liveImplementation.settings as s
from geopy.distance import geodesic
from sklearn.preprocessing import MinMaxScaler
import random
from math import radians, sin, cos, sqrt, atan2

def countInstances(columnm, value, dataframe):
    return dataframe.loc[dataframe[columnm] == value]

def calcPartPerc(part, whole):
    return round((len(part)/len(whole))*100,4)

def Fit_Scaler_To_Data(df):
    scaler = MinMaxScaler()
    features_to_scale = ['LAT', 'LON', 'SOG', 'COG']
    return scaler.fit(df[features_to_scale])

def Remove_Random_COG():
    Limit = 50000

    RNRN = random.sample(range(1, Limit-1), 10000)
    print(np.sort(RNRN))
    print(len(np.unique(RNRN)))

    df = pd.read_csv('data/AIS_2023_01_01.csv', nrows=Limit)

    for x in range(len(RNRN)):
        df.iloc[RNRN[x], df.columns.get_loc('COG')] = None

    df.to_csv('data/skovl.csv')

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

def interpolater(datapath):
    df = pd.read_csv(datapath, nrows=s.readLimit)
    df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)
    df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
    df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)
    
    # # Check if Heading column exists
    if 'Heading' in df.columns:
        mapping_dict = df.set_index('MMSI')['VesselName'].to_dict()
        df = df.drop(columns=['VesselName', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
    
    frequency = s.timeIntervals

    df.set_index('BaseDateTime', inplace=True)
    grouped = df.groupby('MMSI')
    interpolated_data = []

    for mmsi, group in tqdm(grouped, desc="Processing vessels"):
        resampled = group.resample(frequency).first()
        resampled[['LAT', 'LON']] = resampled[['LAT', 'LON']].interpolate(method='linear')
        resampled['COG'] = resampled['COG'].ffill()
        resampled['Heading'] = resampled['Heading'].ffill()
 
        # Calculate speeds for original data points
        speeds = []
        for i in range(1, len(group)):
            if not pd.isna(group.iloc[i]['LAT']) and not pd.isna(group.iloc[i-1]['LAT']):
                lat1, lon1 = group.iloc[i-1]['LAT'], group.iloc[i-1]['LON']
                lat2, lon2 = group.iloc[i]['LAT'], group.iloc[i]['LON']
                distance_km = geodesic((lat1, lon1), (lat2, lon2)).kilometers
                time_diff_hours = (group.index[i] - group.index[i-1]).total_seconds() / 3600
                speed_knots = distance_km / time_diff_hours / 1.852
                speeds.append((group.index[i-1], group.index[i], speed_knots))

        # Assign constant speed to interpolated points
        for start_time, end_time, speed in speeds:
            mask = (resampled.index > start_time) & (resampled.index < end_time)
            resampled.loc[mask, 'SOG'] = speed

        resampled['MMSI'] = mmsi
        interpolated_data.append(resampled)

    interpolated_df = pd.concat(interpolated_data)
    interpolated_df.reset_index(inplace=True)

    print('Boats: ',len(interpolated_df['MMSI']))
    print('Unique boats: ',len(interpolated_df['MMSI'].unique()))

    return interpolated_df, mapping_dict

def convert_to_seconds(df):
    df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
    df['BaseDateTime'] = df['BaseDateTime'].dt.hour * 3600 + df['BaseDateTime'].dt.minute * 60 + df['BaseDateTime'].dt.second

def add_time(output_df):
    df_time = pd.read_csv('data/AIS_2023_01_01.csv')
    df_time.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)
    df_time.drop_duplicates(subset=['MMSI'], keep='first', inplace=True)

    convert_to_seconds(df_time)
    df_time.rename(columns={'BaseDateTime': 'time_seconds'}, inplace=True)
    df_time.drop(columns=['LAT', 'LON', 'SOG', 'COG'], inplace=True)

    convert_to_seconds(output_df)

    heading = output_df['Heading']
    output_df.drop(columns=['Heading'], inplace=True)

    output_df = pd.merge(output_df, df_time, on='MMSI')
    output_df['BaseDateTime'] += output_df['time_seconds']
    output_df.drop(columns=['time_seconds'], inplace=True)

    output_df['Heading'] = heading
    output_df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)

    output_df['BaseDateTime'] = pd.to_datetime(output_df['BaseDateTime'], unit='s', origin='2023-01-01')
    output_df.rename(columns={'VesselName_x': 'VesselName'}, inplace=True)

    return output_df
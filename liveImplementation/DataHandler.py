import pandas as pd
import numpy as np
from tqdm import tqdm
import globalVariables as globals
from geopy.distance import geodesic
from sklearn.preprocessing import MinMaxScaler
import random

def countInstances(columnm, value, dataframe):
    return dataframe.loc[dataframe[columnm] == value]

def calcPartPerc(part, whole):
    return round((len(part)/len(whole))*100)

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



def interpolater():
    df = pd.read_csv("../data/filtered.csv", nrows=globals.readLimit)
    df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)
    df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
    df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)
    
    # # Check if Heading column exists
    if 'Heading' in df.columns:
        mapping_dict = df.set_index('MMSI')['VesselName'].to_dict()
        df = df.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
        

    frequency = '10S'

    df.set_index('BaseDateTime', inplace=True)
    grouped = df.groupby('MMSI')
    interpolated_data = []

    for mmsi, group in tqdm(grouped, desc="Processing vessels"):
        resampled = group.resample(frequency).first()
        resampled[['LAT', 'LON']] = resampled[['LAT', 'LON']].interpolate(method='linear')
        resampled['COG'] = resampled['COG'].ffill()

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
    # print mmsi of the fastest ship
    print(interpolated_df.loc[interpolated_df['SOG'].idxmax()]['MMSI'])
    # print fastest speed
    print(interpolated_df['SOG'].max())

    return interpolated_df, mapping_dict

def add_time(output_df):
    # Read the data from another CSV file with a limit of 'limit' rows
    limit = 50000
    df_time = pd.read_csv('../data/filtered.csv',nrows=limit)
    df_time = df_time.sort_values(by=['MMSI', 'BaseDateTime']).drop_duplicates(subset=['MMSI'], keep='first')

    # Convert 'BaseDateTime' to seconds after midnight and rename the column to 'time_seconds'
    df_time['BaseDateTime'] = pd.to_datetime(df_time['BaseDateTime'])
    df_time['BaseDateTime'] = df_time['BaseDateTime'].dt.hour * 3600 + df_time['BaseDateTime'].dt.minute * 60 + df_time['BaseDateTime'].dt.second
    df_time = df_time.rename(columns={'BaseDateTime': 'time_seconds'})
    df_time = df_time.drop(columns=['LAT', 'LON', 'SOG', 'COG'])
    
    output_df = output_df.sort_values(by=['MMSI', 'BaseDateTime'])
    output_df['BaseDateTime'] = pd.to_datetime(output_df['BaseDateTime'])
    output_df['BaseDateTime'] = output_df['BaseDateTime'].dt.hour * 3600 + output_df['BaseDateTime'].dt.minute * 60 + output_df['BaseDateTime'].dt.second
    
    # Merge the two dataframes
    output_df = pd.merge(output_df, df_time, on='MMSI')
    output_df['BaseDateTime'] = output_df['BaseDateTime'] + output_df['time_seconds']
    output_df = output_df.drop(columns=['time_seconds'])
    output_df = output_df.sort_values(by=['MMSI', 'BaseDateTime'])
    # Convert seconds after midnight to datetime format starting from 2023-01-01
    output_df['BaseDateTime'] = pd.to_datetime(output_df['BaseDateTime'], unit='s', origin='2023-01-01')
    # drop Heading,VesselName_y,IMO,CallSign,VesselType,Status,Length,Width,Draft,Cargo,TransceiverClass from output_df
    output_df = output_df.drop(columns=['Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
    #rename VesselName_x to VesselName
    output_df = output_df.rename(columns={'VesselName_x': 'VesselName'})
    
    return output_df
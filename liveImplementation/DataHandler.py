import pandas as pd
import numpy as np
from tqdm import tqdm
import globalVariables as globals
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
    df = pd.read_csv("../data/AIS_2023_01_01.csv", nrows=globals.readLimit)
    df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)
    df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
    df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)
    
    # # Check if Heading column exists
    if 'Heading' in df.columns:
        df = df.drop(columns=['Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
        mapping_dict = df.set_index('MMSI')['VesselName'].to_dict()

    frequency = '10S' 

    df.set_index('BaseDateTime', inplace=True)
    grouped = df.groupby('MMSI')
    interpolated_data = []

    for mmsi, group in tqdm(grouped, desc="Processing vessels"):
        resampled = group.resample(frequency).first()
        resampled[['LAT', 'LON', 'SOG']] = resampled[['LAT', 'LON', 'SOG']].interpolate(method='linear')
        resampled = resampled.apply(pd.to_numeric, errors='coerce')
        interpolated = resampled
        interpolated['COG'] = interpolated['COG'].ffill()
        interpolated['MMSI'] = mmsi
        interpolated_data.append(interpolated)
    interpolated_df = pd.concat(interpolated_data)
    interpolated_df.reset_index(inplace=True)
    
    return interpolated_df, mapping_dict

def add_time(output_df):
    # Read the data from another CSV file with a limit of 'limit' rows
    limit = 50000
    df_time = pd.read_csv('../data/AIS_2023_01_01.csv',nrows=limit)
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
    return output_df
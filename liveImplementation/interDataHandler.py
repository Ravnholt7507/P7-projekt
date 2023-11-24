import pandas as pd
import numpy as np
from tqdm import tqdm

def cleanseData(timeIntervals): 

    print("Cleaning data...")
    file_path = '../data/AIS_2023_01_01.csv'
    n_rows = 50000
    df = data_loader(file_path, n_rows)   
    df = interpolater(df, timeIntervals)
    dataAsDataFrame = pd.DataFrame(df)
    #group dataframe object by MMSI:
    groupedData = dataAsDataFrame.groupby(0)
    return groupedData

def convert_dt_to_sec(df, n_rows):

    for i in range(n_rows):
        df[i][1] = int(df[i][1][11:13])*3600 + int(df[i][1][14:16])*60 + int(df[i][1][17:])
    return df

def data_loader(file_path, n_rows):
    # 'Timestamp', 'MMSI', 'Latitude', 'Longitude', 'SOG', 'COG'
    fields = [0, 1, 2, 3, 4, 5]
    # read in csv file
    df = pd.read_csv(file_path, skipinitialspace=True, usecols=fields, nrows=n_rows)

    # get rid of nan rows (in speed and course) - could just set to -1
    df = df.dropna()

    #sort by MMSI, then by time/date

    #remove all mmsi's with SOG > 5
    #df = df[df['SOG'] > 5.0]
    
    # remove elements with only 1 mmsi entry
    counts = df.value_counts('MMSI')

    for name, count in counts.items():
        if  count == 4 or count == 3 or count == 2 or count == 1:
            df = df[df['MMSI'] != name]

    df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)
    df.to_csv('sorted_data.csv', index=False, mode='w')
    # change dataframe to numpy array
    df = df.values
    # new number of rows and columns
    n_rows, n_cols = df.shape
    return convert_dt_to_sec(df, n_rows)

def interpolater(df: np.ndarray, timeIntervals):

    print("Interpolating data...")
    
    timeIntervals = (str(timeIntervals) + "S")
    df = pd.DataFrame(df, columns=['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG'])
    interpolated_dfs = []
    i = 0

    length = len(df)-1
    for i in tqdm(range(length)):
        group = df.iloc[i:i+2]
        
        #check if mmsi's are the same
        if group.iloc[0]['MMSI'] == group.iloc[1]['MMSI']:
            group.set_index('BaseDateTime', inplace=True)
            group.index = pd.to_timedelta(group.index, unit='s')
            group = group.infer_objects(copy=False)
            resampled_group = group.resample(timeIntervals).mean().interpolate(method='linear')
            resampled_group.reset_index(inplace=True)
            resampled_group['BaseDateTime'] = resampled_group['BaseDateTime'].dt.total_seconds()
            interpolated_dfs.append(resampled_group)
    
    interpolated_df = pd.concat(interpolated_dfs)
    # Convert mmsi and time back to int
    interpolated_df['MMSI'] = interpolated_df['MMSI'].astype(int)
    interpolated_df['BaseDateTime'] = interpolated_df['BaseDateTime'].astype(int)
    
    # Fill in missing values 
    interpolated_df = interpolated_df.ffill().bfill()
    interpolated_df = interpolated_df[['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG']]    
    interpolated_df.to_csv('../data/interpolated_data.csv', index=False, mode='w')
    interpolated_data = interpolated_df.to_numpy()

    return interpolated_data
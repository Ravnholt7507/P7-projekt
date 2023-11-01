import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def convert_dt_to_sec(df, n_rows):

    for i in range(n_rows):
        df[i][1] = int(df[i][1][11:13])*3600 + int(df[i][1][14:16])*60 + int(df[i][1][17:])
    return df
"""
    i = 0
    while i in range(n_rows):
        end = False
        temp = []
        start = i
        try:
            while df[i+1][0] == df[i][0]:
                temp.append(df[i][1])
                i += 1
                end = True
        except: pass

        if end is True:
            temp.append(df[i][1])
            diff_array = np.diff(temp)

            df[start][1] = 0
            df[start+1:i+1, 1] = diff_array
        i += 1
"""

def group_data_by_mmsi(df):
    MMSI_Values = df[:, 0]
    i = 0

    for count, k in enumerate(MMSI_Values):
        try:
            if MMSI_Values[count + 3] == k:
                i+=1
        except:
            pass
    SizeOfTrain = i

    x_train = np.empty([SizeOfTrain, 5, 6])
    y_train = np.empty([SizeOfTrain, 6])

    i = 0
    for count, k in enumerate(MMSI_Values):
        try:
            if MMSI_Values[count + 3] == k:
                y_train[i][:] = df[count + 0][:]
                x_train[i][0][:] = df[count + 1][:]
                x_train[i][1][:] = df[count + 2][:]
                x_train[i][2][:] = df[count + 3][:]
                x_train[i][3][:] = df[count + 4][:]
                x_train[i][4][:] = df[count + 5][:]
                i += 1
        except:
            pass
    
    #Remove MMSI for train data and everything but lat and long for target data
    x_train = x_train[0:i-1, :, [1,2,3,4,5]] #Remove MMSI
    y_train = y_train[0:i-1, [2,3]] #Keep longitude and latitude
    # splice data for training and testing
    train_length = int(i * 0.8)
    y_test = y_train[train_length:, :]
    x_test = x_train[train_length:, :, :]

    y_train = y_train[:train_length + 1, :]
    x_train = x_train[:train_length + 1, :, :]
    return x_train, y_train, x_test, y_test

def data_normalizer(x_train, x_test, y_train, y_test):
    
    x_train_reshaped = x_train.reshape((-1, x_train.shape[-1]))
    x_test_reshaped = x_test.reshape((-1, x_test.shape[-1]))

    # Normalize the data
    x_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()

    x_train_reshaped = x_scaler.fit_transform(x_train_reshaped)
    x_test_reshaped = x_scaler.transform(x_test_reshaped)

    y_train = y_scaler.fit_transform(y_train)
    y_test = y_scaler.transform(y_test)

    x_train = x_train_reshaped.reshape(x_train.shape)
    x_test = x_test_reshaped.reshape(x_test.shape)

    return x_train, x_test, y_train, y_test, x_scaler, y_scaler

def data_denomalizer(data, scaler):
    return scaler.inverse_transform(data)

def data_loader(file_path, n_rows):
    # 'Timestamp', 'MMSI', 'Latitude', 'Longitude', 'SOG', 'COG'
    fields = [1, 0, 2, 3, 4, 5]
    # read in csv file
    df = pd.read_csv(file_path, skipinitialspace=True, usecols=fields, nrows=n_rows)

    # get rid of nan rows (in speed and course) - could just set to -1
    df = df.dropna()

    #sort by MMSI, then by time/date

    #remove all mmsi's with SOG > 5
    df = df[df['SOG'] > 5.0]
    
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

def interpolater(df: np.ndarray):
    df = pd.DataFrame(df, columns=['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG'])
    interpolated_dfs = []
    i = 0

    while i < len(df)-1 :
        group = df.iloc[i:i+2]
        
        #check if mmsi's are the same
        if group.iloc[0]['MMSI'] == group.iloc[1]['MMSI']:
            group.set_index('BaseDateTime', inplace=True)
            group.index = pd.to_timedelta(group.index, unit='s')
            group = group.astype({'LAT': 'float32', 'LON': 'float32', 'SOG': 'float32', 'COG': 'float32'})
            group = group.infer_objects(copy=False)
            resampled_group = group.resample('30S').mean().interpolate(method='linear')
            resampled_group.reset_index(inplace=True)
            resampled_group['BaseDateTime'] = resampled_group['BaseDateTime'].dt.total_seconds()
            interpolated_dfs.append(resampled_group)
        i += 1
    
    interpolated_df = pd.concat(interpolated_dfs)
    interpolated_df = interpolated_df.ffill().bfill()
    interpolated_df = interpolated_df[['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG']]
    interpolated_df.to_csv('interpolated_data.csv', index=False, mode='w')
    interpolated_data = interpolated_df.to_numpy()

    return interpolated_data

import pandas as pd 
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM,  LeakyReLU
import matplotlib.pyplot as plt
from keras import backend
import math
from sklearn.preprocessing import MinMaxScaler


def data_loader(file_path, n_rows):
    # 'Timestamp', 'MMSI', 'Latitude', 'Longitude', 'SOG', 'COG'
    fields = [1, 0, 2, 3, 4, 5]
    # read in csv file
    df = pd.read_csv(file_path, skipinitialspace=True, usecols=fields, nrows=n_rows)

    # get rid of nan rows (in speed and course) - could just set to -1
    df = df.dropna()

    # sort by MMSI, then by time/date
    df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)

    # Filter data so that only groups who have 4 or more Rows are shown
    # Extract the first 4 rows per group
    df = df.groupby(['MMSI']).filter(lambda x: len(x) >= 4)

    # change dataframe to numpy array
    df = df.values

    # new number of rows and columns
    n_rows, n_cols = df.shape
    return convert_dt_to_sec(df, n_rows), n_rows, n_cols

def convert_dt_to_sec(df, n_rows):

    for i in range(n_rows):
        df[i][1] = int(df[i][1][11:13])*3600 + int(df[i][1][14:16])*60 + int(df[i][1][17:])

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
    return df

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

    x_train = np.empty([SizeOfTrain, 3, 6])
    y_train = np.empty([SizeOfTrain, 6])

    i = 0
    for count, k in enumerate(MMSI_Values):
        try:
            if MMSI_Values[count + 3] == k:
                y_train[i][:] = df[count + 0][:]
                x_train[i][0][:] = df[count + 1][:]
                x_train[i][1][:] = df[count + 2][:]
                x_train[i][2][:] = df[count + 3][:]
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
    # Reshape the data
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

def model_maker(num_features = 5, num_timesteps = 3):
    # create model
    model = Sequential()
    model.add(LSTM(32, return_sequences=True, input_shape=(num_timesteps, num_features)))
    model.add(LSTM(16, return_sequences=True))
    model.add(LSTM(8))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Dense(2))
    model.compile(loss=rmse, optimizer='adam')
    return model

def rmse(y_true, y_pred):
    return backend.sqrt(backend.mean(backend.square(y_true - y_pred), axis=-1))

def plot_data(history):
    plt.figure(1)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])

    plt.title('AIS: Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc='upper right')
    plt.show()

def Distance(prediction, target):

    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """

    lat1 = prediction[0]
    lon1 = prediction[1]
    lat2 = target[0]
    lon2 = target[1]

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371.0 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def Average(lst):
    return sum(lst) / len(lst)

def data_denomalizer(data, scaler):
    return scaler.inverse_transform(data)

def main():
    file_path = 'ann/data.csv'
    n_rows = 200000
    BATCH_SIZE = 10
    NUM_EPOCHS = 10
    df, n_rows, n_cols = data_loader(file_path, n_rows)
    x_train, y_train, x_test, y_test = group_data_by_mmsi(df)
    print(y_test[0])
    x_train, x_test, y_train, y_test, x_scaler, y_scaler = data_normalizer(x_train, x_test, y_train, y_test)
    model = model_maker()
    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS, validation_split=0.20)
    prediction = model.predict(x_test)

    #Evaluate the Model
    scores = model.evaluate(x_test, y_test, verbose=0)
    print('\n%s: %f\n' % ("rmse", scores))

    plot_data(history)

    #Denormalize the data
    y_test_denormalized, prediction_denormalized = data_denomalizer(y_test, y_scaler), data_denomalizer(prediction, y_scaler)
    print("Prediction: ", prediction_denormalized[0], "Actual: ", y_test_denormalized[0])
    print(Distance(prediction_denormalized[0], y_test_denormalized[0]))

    distanceErrors = []
    for x in range(len(prediction_denormalized)):
        distanceErrors.append(Distance(prediction_denormalized[x], y_test_denormalized[x]))
        

    print("Average Distance Error: ", Average(distanceErrors), "km")

if __name__ == "__main__":
    main()

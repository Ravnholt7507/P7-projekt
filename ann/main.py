import pandas as pd
import os
import numpy as np
import torch.nn as nn
import torch.optim as optim
from evaluation import plot_data, Distance, Average
from data_processing import data_loader, group_data_by_mmsi, data_normalizer, data_denomalizer, interpolater
from models import cnn_and_lstm_model_maker, lstm_model_maker, big_cnn_and_lstm_model_maker, cnn_model_maker
from Seq2Seq.training import train
from Seq2Seq.Preprocessing import normalize
from Seq2Seq.Dataloaders import getDataLoaders
from Seq2Seq.Models import getModel
from Seq2Seq.testing import testing


def read_data(file_path, n_rows):
    df = data_loader(file_path, n_rows)
    df = interpolater(df)
    return df


def main():
    file_path = 'ann/data.csv'
    n_rows = 1000000
    BATCH_SIZE = 10
    NUM_EPOCHS = 50
    if os.path.exists('interpolated_data.csv'):
        df = pd.read_csv('interpolated_data.csv')
        df = df.values
    else:
        df = read_data(file_path, n_rows)
    x_train, y_train, x_test, y_test = group_data_by_mmsi(df)

    x_train, x_test, y_train, y_test, x_scaler, y_scaler = data_normalizer(x_train, x_test, y_train, y_test)
    model = cnn_and_lstm_model_maker(num_features = 5, num_timesteps = 5)
 
    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS, validation_split=0.20)
    prediction = model.predict(x_test)

    #Evaluate the Model
    scores = model.evaluate(x_test, y_test, verbose=0)
    print('\n%s: %f\n' % ("rmse", scores))

    #Denormalize the data
    y_test_denormalized, prediction_denormalized = data_denomalizer(y_test, y_scaler), data_denomalizer(prediction, y_scaler)
    print("Prediction: ", prediction_denormalized[0], "Actual: ", y_test_denormalized[0])
    print(Distance(prediction_denormalized[0], y_test_denormalized[0]))

    distanceErrors = []
    for x in range(len(prediction_denormalized)):
        distanceErrors.append(Distance(prediction_denormalized[x], y_test_denormalized[x]))
        

    print("Average Distance Error: ", Average(distanceErrors), "km")

def test_main():
    num_timesteps = 10

    df = pd.read_csv('interpolated_data.csv')
    
    counts = df.value_counts('MMSI')

    for name, count in counts.items():
        if count < num_timesteps:
            df = df[df['MMSI'] != name]
    
    df = df.groupby('MMSI')
    df = df.head(num_timesteps)
    df = df.values

    #make df 3 dimensional
    df = df.reshape((-1, num_timesteps, 6))
    print(df.shape)


    split = int(0.8 * len(df))
    x_train = df[:split, :-1, [1,2,3,4,5]]
    y_train = df[:split, [num_timesteps-2],[2,3]]
    x_test = df[split:, :-1, [1,2,3,4,5]]
    y_test = df[split:, [num_timesteps-2],[2,3]]
    
    #reshape tests
    x_train = x_train.reshape((-1, num_timesteps - 1, 5))
    y_train = y_train.reshape((-1, 2))
    x_test = x_test.reshape((-1, num_timesteps - 1, 5))
    y_test = y_test.reshape((-1, 2))
    
    #normalize data
    x_train, x_test, y_train, y_test, x_scaler, y_scaler = data_normalizer(x_train, x_test, y_train, y_test)

    #make model
    model = cnn_and_lstm_model_maker(num_features = 5, num_timesteps = num_timesteps - 1)
    BATCH_SIZE = 10
    NUM_EPOCHS = 500
    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS, validation_split=0.20)
    prediction = model.predict(x_test)

    #Evaluate the Model
    scores = model.evaluate(x_test, y_test, verbose=0)
    print('\n%s: %f\n' % ("rmse", scores))

    #Denormalize the data
    y_test_denormalized, prediction_denormalized = data_denomalizer(y_test, y_scaler), data_denomalizer(prediction, y_scaler)
    print("Prediction: ", prediction_denormalized[0], "Actual: ", y_test_denormalized[0])
    print(Distance(prediction_denormalized[0], y_test_denormalized[0]))

    distanceErrors = []
    for x in range(len(prediction_denormalized)):
        distanceErrors.append(Distance(prediction_denormalized[x], y_test_denormalized[x]))
    
    print("Average Distance Error: ", Average(distanceErrors), "km")

def test_test_main():
    # pull only specific columns out

# 'MMSI', 'Timestamp', 'Latitude', 'Longitude', 'SOG', 'COG'
    fields = [0, 1, 2, 3, 4, 5]
    n_rows = 20000
    df = pd.read_csv('C:\\Users\\mikkel\\Documents\\GitHub\\P7-projekt\\ann\\data\\interpolated_complete.csv', skipinitialspace=True, usecols=fields, nrows=n_rows, on_bad_lines='skip')
    df = df[['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'COG']]
    df, scaler = normalize(df)
    modelname = 'Transformer'
    Train_Loader, Valid_Loader, Test_Loader = getDataLoaders(df, input_sequence_length=20, output_sequence_length=3)
    train(modelname, Train_Loader, Valid_Loader)
    testing(modelname, Test_Loader, df, scaler)

if __name__ == "__main__":
    test_test_main()

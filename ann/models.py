import tensorflow as tf
import math
from keras.models import Sequential
from keras.layers import Dense, LSTM,  LeakyReLU, Conv1D, MaxPooling1D, Flatten
from keras import backend

#3 layer CNN +LSTM 
def cnn_and_lstm_model_maker(num_features = 5, num_timesteps = 3):
    cnn_model = Sequential()
    cnn_model.add(Conv1D(filters=32, kernel_size=2, activation='relu', input_shape=(num_timesteps, num_features), padding='same'))
    cnn_model.add(MaxPooling1D(pool_size=2))
    cnn_model.add(Conv1D(filters=64, kernel_size=2, activation='relu', padding='same'))
    model_lstm = Sequential()
    model_lstm.add(LSTM(128, return_sequences=True))
    model_lstm.add(LSTM(256))
    model_lstm.add(LeakyReLU(alpha=0.001))
    combined_model = Sequential()
    combined_model.add(cnn_model)
    combined_model.add(model_lstm)
    combined_model.add(Dense(2))
    combined_model.compile(loss=dist_error, optimizer='adam')
    return combined_model

def big_cnn_and_lstm_model_maker(num_features = 5, num_timesteps = 3):
    cnn_model = Sequential()
    cnn_model.add(Conv1D(filters=128, kernel_size=1, activation='relu', input_shape=(num_timesteps, num_features)))
    cnn_model.add(MaxPooling1D(pool_size=1))
    cnn_model.add(Conv1D(filters=64, kernel_size=1, activation='relu'))
    cnn_model.add(MaxPooling1D(pool_size=1))
    cnn_model.add(Conv1D(filters=32, kernel_size=1, activation='relu'))
    cnn_model.add(MaxPooling1D(pool_size=1))
    model_lstm = Sequential()
    model_lstm.add(LSTM(32, return_sequences=True))
    model_lstm.add(LSTM(16, return_sequences=True))
    model_lstm.add(LSTM(8))
    model_lstm.add(LeakyReLU(alpha=0.01))
    combined_model = Sequential()
    combined_model.add(cnn_model)
    combined_model.add(model_lstm)
    combined_model.add(Dense(2))
    combined_model.compile(loss=rmse, optimizer='adam')
    return combined_model

def cnn_model_maker(num_features = 5, num_timesteps = 3):
    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=3, activation='relu',  input_shape=(num_timesteps, num_features), padding='same'))
    #model.add(MaxPooling1D(pool_size=2))

    model.add(Conv1D(filters=128, kernel_size=3, activation='relu', padding='same'))
    #model.add(MaxPooling1D(pool_size=2))

    model.add(Flatten())
    model.add(Dense(256, activation='relu'))

    model.add(Dense(2))

    model.compile(loss=rmse, optimizer='adam')
    return model

#4 layer LSTM
def lstm_model_maker(num_features = 5, num_timesteps = 3):
    # create model
    model = Sequential()
    model.add(LSTM(32, return_sequences=True, input_shape=(num_timesteps, num_features)))
    model.add(LSTM(16, return_sequences=True))
    model.add(LSTM(8))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Dense(2))
    model.compile(loss=dist_error, optimizer='adam')
    return model

#error function
def rmse(y_true, y_pred):
    return backend.sqrt(backend.mean(backend.square(y_true - y_pred), axis=-1))

#error function based on distance
def dist_error(y_true, y_pred):
    y_true = tf.cast(y_true, dtype=tf.float32) 
    y_pred = tf.cast(y_pred, dtype=tf.float32)  

    lat1 = y_pred[:, 0]
    lon1 = y_pred[:, 1]
    lat2 = y_true[:, 0]
    lon2 = y_true[:, 1]

    
    lat1_rad = tf.multiply(lat1, math.pi / 180.0)
    lon1_rad = tf.multiply(lon1, math.pi / 180.0)
    lat2_rad = tf.multiply(lat2, math.pi / 180.0)
    lon2_rad = tf.multiply(lon2, math.pi / 180.0)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = tf.math.sin(dlat/2)**2 + tf.math.cos(lat1_rad) * tf.math.cos(lat2_rad) * tf.math.sin(dlon/2)**2
    c = 2 * tf.math.atan2(tf.math.sqrt(a), tf.math.sqrt(1-a))
    r = 6371.0 

    return backend.sqrt(backend.mean(backend.square(c * r), axis=-1))

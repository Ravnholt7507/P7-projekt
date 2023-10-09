from keras.models import Sequential
from keras.layers import Dense, LSTM,  LeakyReLU, Conv1D, MaxPooling1D, Dropout
from keras import backend

#3 layer CNN +LSTM 
def cnn_and_lstm_model_maker(num_features = 5, num_timesteps = 3):
    cnn_model = Sequential()
    cnn_model.add(Conv1D(filters=32, kernel_size=2, activation='relu', input_shape=(num_timesteps, num_features)))
    cnn_model.add(MaxPooling1D(pool_size=2))
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

def big_cnn_and_lstm_model_maker(num_features = 5, num_timesteps = 3):
    cnn_model = Sequential()
    cnn_model.add(Conv1D(filters=128, kernel_size=2, activation='relu', input_shape=(num_timesteps, num_features)))
    cnn_model.add(MaxPooling1D(pool_size=2))
    cnn_model.add(Conv1D(filters=64, kernel_size=2, activation='relu'))
    cnn_model.add(MaxPooling1D(pool_size=2))
    cnn_model.add(Conv1D(filters=32, kernel_size=2, activation='relu'))
    cnn_model.add(MaxPooling1D(pool_size=2))
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


#4 layer LSTM
def lstm_model_maker(num_features = 5, num_timesteps = 3):
    # create model
    model = Sequential()
    model.add(LSTM(32, return_sequences=True, input_shape=(num_timesteps, num_features)))
    model.add(LSTM(16, return_sequences=True))
    model.add(LSTM(8))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Dense(2))
    model.compile(loss=rmse, optimizer='adam')
    return model

#error function
def rmse(y_true, y_pred):
    return backend.sqrt(backend.mean(backend.square(y_true - y_pred), axis=-1))
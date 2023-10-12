from evaluation import plot_data, Distance, Average
from data_processing import data_loader, group_data_by_mmsi, data_normalizer, data_denomalizer
from models import cnn_and_lstm_model_maker, lstm_model_maker, big_cnn_and_lstm_model_maker, cnn_model_maker

def main():
    file_path = 'ann/data.csv'
    n_rows = 100000
    BATCH_SIZE = 10
    NUM_EPOCHS = 200
    df, n_rows, _ = data_loader(file_path, n_rows)
    x_train, y_train, x_test, y_test = group_data_by_mmsi(df)
    x_train, x_test, y_train, y_test, x_scaler, y_scaler = data_normalizer(x_train, x_test, y_train, y_test)
    model = lstm_model_maker(num_features = 5, num_timesteps = 3)
 
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

if __name__ == "__main__":
    main()

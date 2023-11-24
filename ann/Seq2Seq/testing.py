from Seq2Seq.Dataloaders import getDataLoaders
from Seq2Seq.Models import getModel
from Seq2Seq.haversine_loss import haversine
from Seq2Seq.Preprocessing import GetMinMaxCoords, denormalize
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from tqdm import tqdm

def testing(modelname, Test_AISDataLoader, df, scaler):
    model = getModel(modelname)
    model.load_state_dict(torch.load(f'ann/saved_models/{modelname}.pth'))
    model.eval()
    
    lat_min, lat_max, lon_min, lon_max = GetMinMaxCoords(df)

    test_loss_haversine = 0
    test_loss_rmse = 0
    criterion = nn.MSELoss()
    predicted_lat_lon = []

    model.eval()
    with torch.no_grad():
        for batch in Test_AISDataLoader:
            inputs, targets = batch
            outputs = model(inputs)

            test_loss_haversine += haversine(outputs, targets, lat_min, lat_max, lon_min, lon_max).item()
            test_loss_rmse += criterion(outputs, targets).item()

    avg_haversine = test_loss_haversine / len(Test_AISDataLoader)
    avg_rmse = test_loss_rmse / len(Test_AISDataLoader)

    print("Haversine loss in Km: ", avg_haversine)
    print("RMSE loss: ", avg_rmse)
    input, target = next(iter(Test_AISDataLoader))
    prediction = model(input)
    prediction = prediction.detach()

    input = denormalize(scaler, input)
    target = denormalize(scaler, target)
    prediction = denormalize(scaler, prediction)

    # Re-implementing the plotting functions for Matplotlib and Geopandas

    import numpy as np
    import matplotlib.pyplot as plt

    index = 1
    #connect the last element of the input trajectory as the first element of target and prediction
    connector = input[:, -1:, :]
    target = np.concatenate((connector, target), axis=1)
    prediction = np.concatenate((connector, prediction), axis=1)

    # Extract latitude and longitude
    input_lat_lon = input[index,:,:2]
    target_lat_lon = target[index,:,:2]
    predicted_lat_lon = prediction[index,:,:2]

    plt.plot(input_lat_lon[:, 0], input_lat_lon[:, 1], color='blue', alpha=0.5, label='Input')
    plt.plot(target_lat_lon [:, 0], target_lat_lon [:, 1], color='green', alpha=0.5, label='Target')
    plt.plot(predicted_lat_lon[:, 0], predicted_lat_lon[:, 1], color='red', alpha=0.5, label='Predicted')
    # Plot with Matplotlib

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Adding gridlines

    plt.title('Trajectories with Matplotlib')
    plt.legend()
    plt.show()
from Seq2Seq.Dataloaders import getDataLoaders
from Seq2Seq.Models import getModel
from Seq2Seq.haversine_loss import haversine
from Seq2Seq.Preprocessing import GetMinMaxCoords
import torch
import torch.nn as nn
import torch.optim as opt
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.pyplot as plt
from tqdm import tqdm

def train(modelname, Train_AISDataLoader, Valid_AISDataLoader):

    model = getModel(modelname)

    # Define an optimizer. You can use Adam, which is a good default choice for many applications.
    optimizer = opt.Adam(model.parameters(), lr=0.0005)
    criterion = nn.MSELoss()
    epochs = 20

    # Initialize the scheduler
    from torch.optim.lr_scheduler import ReduceLROnPlateau
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5, verbose=True)

    # Move the model to the GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Initialize variables for plotting
    epoch_counts = []
    valid_losses = []
    train_losses = []


    for epoch in range(epochs):
        model.train()
        loss = 0
        train_loss = 0
        for batch in tqdm(Train_AISDataLoader, desc="Running"):
            inputs, targets = batch  # Assuming each batch returns inputs and targets
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = torch.sqrt(criterion(outputs, targets)) #RootMeanSquare
            train_loss += loss.item()
            #haversine_loss_train += haversine(outputs, targets, lat_min, lat_max, lon_min, lon_max).item()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Evaluate on test data
        model.eval()
        valid_loss = 0
        with torch.no_grad():
            for batch in Valid_AISDataLoader:
                inputs, targets = batch
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)

                #total_loss += haversine(outputs, targets, lat_min, lat_max, lon_min, lon_max).item()
                valid_loss += torch.sqrt(criterion(outputs, targets)).item()

        avg_train_loss = train_loss / len(Train_AISDataLoader)
        avg_valid_loss = valid_loss / len(Valid_AISDataLoader)
        valid_losses.append(avg_valid_loss)
        train_losses.append(avg_train_loss)
        epoch_counts.append(epoch)
        print(f"Epoch: {epoch}, Train Loss: {avg_train_loss}")
        print(f"Epoch: {epoch}, Valid Loss: {avg_valid_loss}")
        # Step the scheduler with the average loss
        scheduler.step(avg_train_loss)

    # Plotting the test loss
    plt.figure(figsize=(5, 4))
    plt.plot(epoch_counts, valid_losses, label='Valid Loss')
    plt.plot(epoch_counts, train_losses, label='Train Loss')
    plt.title('train and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('loss as rmse')
    plt.grid(True)
    plt.legend()
    plt.show()

    torch.save(model.state_dict(), f'ann/saved_models/{modelname}.pth')
from Seq2Seq.Dataloaders import getDataLoaders
from Seq2Seq.transformerEncoder import getModel
from Seq2Seq.haversine_loss import haversine
from Seq2Seq.Preprocessing import GetMinMaxCoords
import torch
import torch.optim as optim
import matplotlib.pyplot as plt
from tqdm import tqdm

def train(df):

    model = getModel()
    print(model)
    lat_max, lat_min, lon_max, lon_min = GetMinMaxCoords(df)
    Train_AISDataLoader, Test_AISDataLoader = getDataLoaders(df, input_sequence_length=10, output_sequence_length=3)

    # Define an optimizer. You can use Adam, which is a good default choice for many applications.
    optimizer = optim.Adam(model.parameters(), lr=0.0003)

    # Move the model to the GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Initialize variables for plotting
    epoch_counts = []
    test_losses = []
    predicted_lat_lon = []

    for epoch in range(0, 31, 1):  # Running 10 epochs, incrementing by 10 each time
        model.train()
        for batch in tqdm(Train_AISDataLoader, desc="Running"):
            inputs, targets = batch  # Assuming each batch returns inputs and targets
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = haversine(outputs, targets, lat_min, lat_max, lon_min, lon_max)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Evaluate on test data
        model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch in Test_AISDataLoader:
                inputs, targets = batch
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)

                total_loss += haversine(outputs, targets, lat_min, lat_max, lon_min, lon_max).item()

                # Record the predicted lat and lon
                predicted_lat_lon.append(outputs[:, :, :2].cpu().detach().numpy())  # Assuming first two features are lat and lon

        avg_test_loss = total_loss / len(Test_AISDataLoader)
        test_losses.append(avg_test_loss)
        epoch_counts.append(epoch)
        print(f"Epoch: {epoch}, Test Loss: {avg_test_loss}")

    # Plotting the test loss
    plt.figure(figsize=(10, 4))
    plt.plot(epoch_counts, test_losses, marker='o')
    plt.title('Test Loss Over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Test Loss')
    plt.grid(True)
    plt.show()
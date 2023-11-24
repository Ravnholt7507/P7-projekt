import numpy as np
from tqdm import tqdm
import torch
from torch.utils.data import Dataset, random_split


class AISDataset(Dataset):
    def __init__(self, dataframe, seq_len=20, pred_len=3):
        self.mmsi = dataframe['MMSI'].values  # Store MMSI values
        self.data = dataframe.iloc[:, 2:].values  # Excludes the 'MMSI' and 'BaseDateTime' column
        self.seq_len = seq_len
        self.pred_len = pred_len

    def __len__(self):
        return len(self.data) - self.seq_len - self.pred_len + 1

    def __getitem__(self, idx):
        start_idx = idx
        end_idx = idx + self.seq_len + self.pred_len

        # Splitting the data into input and target sequences
        input_seq = self.data[start_idx:start_idx + self.seq_len]
        target_seq = self.data[start_idx + self.seq_len:end_idx]

        return torch.tensor(input_seq, dtype=torch.float), torch.tensor(target_seq, dtype=torch.float) #, self.mmsi[start_idx]

# Usage
def getDataLoaders(df, input_sequence_length, output_sequence_length):

    dataset = AISDataset(df, input_sequence_length, output_sequence_length)
    train_size = int(0.7 * len(dataset))
    valid_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - valid_size

    train_dataset, valid_dataset, test_dataset = random_split(dataset, [train_size, valid_size, test_size])

    Train_AISDataLoader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True, drop_last=True, num_workers=2)
    Test_AISDataLoader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=True, drop_last=True, num_workers=2)
    Valid_AISDataLoader = torch.utils.data.DataLoader(valid_dataset, batch_size=32, shuffle=True, drop_last=True, num_workers=2)
    
    return Train_AISDataLoader, Valid_AISDataLoader, Test_AISDataLoader
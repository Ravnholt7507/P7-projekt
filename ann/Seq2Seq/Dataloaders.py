import numpy as np
from tqdm import tqdm
import torch
from torch.utils.data import Dataset, random_split

class AISTrajectoryDataset(Dataset):
    def __init__(self, df, input_sequence_length, output_sequence_length):
        self.sequence_length = input_sequence_length + output_sequence_length
        self.input_sequence_length = input_sequence_length
        self.output_sequence_length = output_sequence_length

        # Sort by MMSI and Timestamp to ensure continuity in sequences
        df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)

        # Group by MMSI and create a list of sequences per MMSI
        self.sequences = self.create_sequences(df, self.sequence_length)

    def create_sequences(self, df, sequence_length):
        sequences = []
        for _, group in tqdm(df.groupby('MMSI'), desc="creating sequences"):
            num_sequences = len(group) - sequence_length + 1
            for i in range(num_sequences):
                sequences.append(group[i:i + sequence_length][['LAT', 'LON', 'SOG', 'COG']].values.astype(np.float32))
        return sequences

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        src = torch.from_numpy(sequence[:self.input_sequence_length])
        trg = torch.from_numpy(sequence[self.input_sequence_length:])
        return src, trg

# Usage
def getDataLoaders(df, input_sequence_length, output_sequence_length):
    dataset = AISTrajectoryDataset(df, input_sequence_length, output_sequence_length)

    train_size = int(0.8*len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

    Train_AISDataLoader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True, drop_last=True, num_workers=2)
    Test_AISDataLoader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=True, drop_last=True, num_workers=2)
    return Train_AISDataLoader, Test_AISDataLoader
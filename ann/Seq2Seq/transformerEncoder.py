import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_length):
        super().__init__()
        self.d_model = d_model
        position = torch.arange(max_length).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_length, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return x

class TransformerModel(nn.Module):
    def __init__(self, feature_size, d_model, nhead, num_layers, output_timesteps, output_features):
        super().__init__()
        self.input_linear = nn.Linear(feature_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, 50)
        encoder_layers = nn.TransformerEncoderLayer(d_model = d_model, nhead = nhead)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.output_linear = nn.Linear(d_model, output_features)
        self.output_timesteps = output_timesteps

    def forward(self, x):
        x = self.input_linear(x)
        x = self.pos_encoder(x)
        x = x.permute(1, 0, 2)
        x = self.transformer_encoder(x)
        x = x.permute(1, 0, 2)
        x = self.output_linear(x)
        output = x[:, -self.output_timesteps:, :]
        return output
    
def getModel():
    # Define the model
    feature_size = 4  # Adjust based on your AIS data features
    d_model = 64     # Size of the feature embeddings
    nhead = 2         # Number of heads in the multiheadattention models
    num_layers = 2    # Number of sub-encoder-layers in the encoder
    output_features = 4   # Number of time steps to predict * number of features
    output_steps = 3

    model = TransformerModel(feature_size, d_model, nhead, num_layers, output_steps,output_features)
    return model
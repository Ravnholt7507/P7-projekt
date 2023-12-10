import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import torch.nn.init as init

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

#lstmseq2seqatt
import torch
import torch.nn as nn
import random

# Bahdanau Attention Mechanism
class BahdanauAttention(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.fc_hidden = nn.Linear(hidden_size, hidden_size)
        self.fc_encoder = nn.Linear(hidden_size, hidden_size)
        self.fc_attention = nn.Linear(hidden_size, 1)

    def forward(self, hidden, encoder_outputs):
        seq_len = encoder_outputs.size(1)
        hidden = hidden[-1]  # Take the last layer hidden state
        hidden = hidden.unsqueeze(1).repeat(1, seq_len, 1)
        energy = torch.tanh(self.fc_hidden(hidden) + self.fc_encoder(encoder_outputs))
        attention = self.fc_attention(energy).squeeze(2)
        return F.softmax(attention, dim=1)

# Encoder with Bidirectional LSTM
class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size, dropout=0, bidirectional=True):
        super().__init__()
        self.bidirectional = bidirectional
        self.hidden_size = hidden_size * 2 if bidirectional else hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True, bidirectional=bidirectional)
        self.dropout = nn.Dropout(dropout)
        self.initialize_lstm_weights()

    def initialize_lstm_weights(self):
        for name, param in self.lstm.named_parameters():
            if 'bias' in name:
                with torch.no_grad():
                    param.zero_()
                    length = param.size(0) // 4
                    param[length:2*length] = 1
            elif 'weight_ih' in name:
                init.xavier_uniform_(param)
            elif 'weight_hh' in name:
                init.orthogonal_(param)

    def forward(self, encoder_inputs):
        outputs, (hidden, cell) = self.lstm(encoder_inputs)
        outputs = self.dropout(outputs)
        
        if self.bidirectional:
            hidden = torch.cat([hidden[-2], hidden[-1]], dim=1).unsqueeze(0)
            cell = torch.cat([cell[-2], cell[-1]], dim=1).unsqueeze(0)
        
        return outputs, (hidden, cell)

# Decoder
class Decoder(nn.Module):
    def __init__(self, input_size, hidden_size, dropout=0):
        super().__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size + hidden_size, hidden_size, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        #self.out = nn.Linear(hidden_size, input_size)
        self.attention = BahdanauAttention(hidden_size)
        self.initialize_lstm_weights()
        self.mlp = nn.Sequential(
          nn.Linear(hidden_size, hidden_size),
          nn.ReLU(),
          nn.Linear(hidden_size, input_size)
          )

    def initialize_lstm_weights(self):
        for name, param in self.lstm.named_parameters():
            if 'bias' in name:
                with torch.no_grad():
                    param.zero_()
                    length = param.size(0) // 4
                    param[length:2*length] = 1
            elif 'weight_ih' in name:
                init.xavier_uniform_(param)
            elif 'weight_hh' in name:
                init.orthogonal_(param)

    def forward(self, initial_input, encoder_outputs, hidden_cell, targets, teacher_force_probability, prediction_length):
        input_at_t = initial_input
        hidden, cell = hidden_cell
        batch_size = initial_input.size(0)
        decoder_sequence_length = prediction_length if targets is None else targets.size(1)
        outputs = torch.zeros(batch_size, decoder_sequence_length, 4)

        for t in range(decoder_sequence_length):
            attention_weights = self.attention(hidden, encoder_outputs)
            context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs).squeeze(1)
            lstm_input = torch.cat((input_at_t, context), dim=1)
            output, (hidden, cell) = self.lstm(lstm_input.unsqueeze(1), (hidden, cell))
            output = self.dropout(output)
            output = self.mlp(output.squeeze(1))
            outputs[:, t, :] = output

            if teacher_force_probability is not None:
                teacher_force = random.random() < teacher_force_probability
                input_at_t = targets[:, t, :] if teacher_force else output
            else:
                input_at_t = output

        return outputs

# Seq2Seq Model
class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def forward(self, encoder_inputs=None, targets=None, teacher_force_probability=None, prediction_length=None):
        encoder_outputs, hidden_cell = self.encoder(encoder_inputs)
        outputs = self.decoder(encoder_inputs[:, -1, :], encoder_outputs, hidden_cell, targets, teacher_force_probability, prediction_length)
        return outputs

def getModel(modelString):
    if modelString == 'Seq2Seq' or modelString == 'seq2Seq':
        model = Seq2Seq(Encoder(input_size=4, hidden_size = 64), Decoder(input_size = 4, hidden_size = 64*2))
    if modelString == 'Transformer' or modelString == 'transformer':
        model = TransformerModel(feature_size=4, d_model=64, nhead=2, num_layers=3, output_timesteps=3, output_features=4)
    return model
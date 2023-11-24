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



class EncoderSimple(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(EncoderSimple, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)

    def forward(self, x):
        outputs, hidden = self.lstm(x)
        return outputs, hidden


class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.hidden_size = hidden_size

    def forward(self, encoder_outputs, decoder_hidden):
        # Attention mechanism to compute context vector
        attn_weights = torch.bmm(encoder_outputs, decoder_hidden.unsqueeze(2)).squeeze(2)
        attn_weights = F.softmax(attn_weights, dim=1)
        context = torch.bmm(attn_weights.unsqueeze(1), encoder_outputs).squeeze(1)
        return context

class DecoderWithAttention(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DecoderWithAttention, self).__init__()
        self.hidden_size = hidden_size
        self.input_transform = nn.Linear(input_size, hidden_size)
        self.attention = Attention(hidden_size)
        self.lstm = nn.LSTM(hidden_size + hidden_size, hidden_size, batch_first=True)  # Input size is doubled due to context vector
        self.out = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden, encoder_outputs):
        x = self.input_transform(x)  # Transform the input to match hidden size
        context = self.attention(encoder_outputs, hidden[0][-1])  # Get context vector from attention module
        lstm_input = torch.cat((x, context.unsqueeze(1)), dim=2)  # Concatenate input with context
        output, hidden = self.lstm(lstm_input, hidden)
        output = self.out(output)
        return output, hidden

class Seq2SeqWithAttention(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(Seq2SeqWithAttention, self).__init__()
        self.input_size = input_size
        self.encoder = EncoderSimple(self.input_size, hidden_size)
        self.decoder = DecoderWithAttention(self.input_size, hidden_size, output_size)

    def forward(self, x, target_length=3):
        encoder_outputs, hidden = self.encoder(x)

        # Prepare the initial input for the decoder
        decoder_input = torch.zeros(x.size(0), 1, self.input_size, device=x.device)

        outputs = []
        for t in range(target_length):
            decoder_output, hidden = self.decoder(decoder_input, hidden, encoder_outputs)
            outputs.append(decoder_output)
            decoder_input = decoder_output

        outputs = torch.cat(outputs, dim=1)
        return outputs




def getModel(modelString):
    if modelString == 'Seq2Seq' or modelString == 'seq2Seq':
        model = Seq2SeqWithAttention(input_size=4, hidden_size=100, output_size=4)
    if modelString == 'Transformer' or modelString == 'transformer':
        model = TransformerModel(feature_size=4, d_model=64, nhead=2, num_layers=3, output_timesteps=3, output_features=4)
    return model
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

timeIntervals = 120
readLimit = 50000
output_CSV = pd.DataFrame()
scaler = MinMaxScaler()
tts = 0
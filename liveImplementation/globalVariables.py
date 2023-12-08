import pandas as pd
import pyttsx3
from sklearn.preprocessing import MinMaxScaler

timeIntervals = 10
readLimit = 50000
output_CSV = pd.DataFrame()
tts = 0
scaler = MinMaxScaler()
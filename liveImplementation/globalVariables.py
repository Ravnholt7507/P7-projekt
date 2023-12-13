import pandas as pd
from sklearn.preprocessing import MinMaxScaler

timeIntervals = 10
readLimit = 50000
output_CSV = pd.DataFrame()
scaler = MinMaxScaler()
tts = 0

targetValues = 0
predictedValues = 0
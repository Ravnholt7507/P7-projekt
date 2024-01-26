import pandas as pd
from sklearn.preprocessing import MinMaxScaler

output_CSV = pd.DataFrame()
scaler = MinMaxScaler()


readLimit = 50000

timeIntervalSeq = ['10S', '20S', '120S']
timeIntervals = '10S'
timeIntervalsInt = int(''.join(filter(str.isdigit, timeIntervals)))

radiusSeq = [0.025, 0.05, 0.075, 0.1]
Radius = 0.075

rateOfTurnSeq = [0.5, 1, 2, 4]
rateOfTurn = 2
pointSpeed = 0.3

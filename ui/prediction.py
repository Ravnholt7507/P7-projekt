import pandas as pd
import numpy as np
import time
import datetime
from datetime import datetime

df = pd.read_csv('boats.csv')

first = df.groupby('MMSI').apply(lambda t: t.iloc[0])
second = df.groupby('MMSI').apply(lambda t: t.iloc[1])

for i in range(len(df['MMSI'].unique())-302):
    print("CURRENT LOCATION: \n")
    print("LAT: ", first.iloc[i]['LAT'])
    print("LON: ", first.iloc[i]['LON'])
    print("SOG: ", first.iloc[i]['SOG'])
    print("COG: ", first.iloc[i]['COG'])
    print("Heading: ", first.iloc[i]['Heading'])
    print("TIME: ", first.iloc[i]['BaseDateTime'], "\n")


    print("CALCULATED VECTOR: \n")
    print("FUTURE LOCATION: \n")
    print("LAT: ", second.iloc[i]['LAT'])
    print("LON: ", second.iloc[i]['LON'])
    print("SOG: ", second.iloc[i]['SOG'])
    print("COG: ", second.iloc[i]['COG'])
    print("Heading: ", second.iloc[i]['Heading'])
    print("TIME: ", second.iloc[i]['BaseDateTime'], "\n")

    print("VECTOR CALCULATION: \n")

    
    parsedPreTime=pd.to_datetime(first.iloc[i]['BaseDateTime'])
    parsedPostTime=pd.to_datetime(second.iloc[i]['BaseDateTime'])
    timeDiff=parsedPostTime-parsedPreTime
    print(timeDiff.total_seconds())    
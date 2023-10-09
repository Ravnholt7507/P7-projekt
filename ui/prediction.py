import pandas as pd
import numpy as np
import time
import datetime
from datetime import datetime
import math
import csv
import map

df = pd.read_csv('boats2.csv')

first = df.groupby('MMSI').apply(lambda t: t.iloc[0])
second = df.groupby('MMSI').apply(lambda t: t.iloc[1])

for i in range(len(df['MMSI'].unique())-302):
    
    print("VESSEL: ", first.iloc[i]['MMSI'])
    
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
    print("Time difference: ", timeDiff.total_seconds(), " seconds")
    
    # Uselss code (angiveligt)    
    # COGrad = 360 * math.pi/180
    # print("COGrad :", COGrad)

    # directX = math.cos(COGrad)
    # directY = math.sin(COGrad)
    
    timeDiffFloat = timeDiff.total_seconds()
    
    predLocX = first.iloc[i]['LAT'] + (first.iloc[i]['SOG']*(timeDiffFloat/60)/60)*first.iloc[i]['COG']/1000
    predLocY = first.iloc[i]['LON'] + (first.iloc[i]['SOG']*(timeDiffFloat/60)/60)*first.iloc[i]['COG']/1000
    
    print('pred LAT',predLocX)
    print('pred LON',predLocY)
    
    array = []
    array.append(first.iloc[i]['MMSI'])
    array.append(predLocX)
    array.append(predLocY)
    
    print("FUTURE LOCATION: \n")
    print("Boat: ", array[0])

with open('predictions.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["MMSI", "LAT", "LON"]
    writer.writerow(field)
    writer.writerow(array)

map.plot()
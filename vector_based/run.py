import prediction
import pandas as pd
import csv

df = pd.read_csv('boats.csv')
ship = df.loc[df['MMSI'] == df.iloc[1]['MMSI']]

predictions = []

def dropAllExceptFirst(ship):
    for i in range(1,len(ship)-1):
        print(i)
        ship = ship.drop(i)
        prediction.predict(ship)
        predictions.append(pd.read_csv('predictions.csv'))
        print(ship)

dropAllExceptFirst(ship)

#print(predictions[0])

#prediction.predict(Ship)
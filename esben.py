import vector_based.collision as collision
import vector_based.prediction as prediction
import vector_based.fuckcleansedata as cleanse
import vector_based.cluster as cluster
import pandas as pd
import csv

cleanse.cleanse()

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

prediction.all_ships()

actual_position = pd.read_csv('data/Collision_boats.csv')
actual_position = actual_position.drop_duplicates(subset='MMSI', keep='first')
skovl = cluster.cluster_ships_kmeans(actual_position, 3)

print(skovl)

with open('data/Collision_predictions.csv', 'w') as tp:
    tp.truncate()

df = pd.read_csv('data/predictions.csv')

empty = False

with open('data/Collision_predictions.csv', 'r') as file:
    csv_dict = [row for row in csv.DictReader(file)]
    if len(csv_dict) == 0:
        print('File is empty')
        empty = True

ship = df
length = len(ship)        

for i in range(length):
    array = []
    array.append(ship.iloc[i]['MMSI'])
    array.append(ship.iloc[i]['BaseDateTime'])
    array.append(ship.iloc[i]['LAT'])
    array.append(ship.iloc[i]['LON'])
    array.append(ship.iloc[i]['SOG'])
    array.append(skovl[i])
    with open('data/clustered_actual_ships.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if i == 0 and empty:
            field = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG', 'Cluster']
            writer.writerow(field)
        writer.writerow(array)

Clusters = pd.read_csv('data/clustered_actual_ships.csv')
fuckdig = Clusters.groupby('Cluster').filter(lambda x: len(x) > 1)
RelevantClusters = fuckdig['Cluster'].unique()

#collision.find_intersection()

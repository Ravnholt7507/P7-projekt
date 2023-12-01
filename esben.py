import vector_based.cleanse_all_collisions as cleanse
import vector_based.prediction as prediction
import vector_based.cluster as cluster
import vector_based.collision as collision
import pandas as pd
from haversine import haversine, Unit
import time

limit = 50000

df2 = pd.read_csv('data/output.csv')
df3 = df2.groupby('MMSI').first().reset_index()
df4 = df2[df2['thresholdExceeded'] == True]
df4 = pd.concat([df3, df4])
ship_data = df4.sort_values(by=['MMSI'])
ship_data = ship_data.drop_duplicates()
ship_data = ship_data.drop(columns=['Unnamed: 0'])

df_time = pd.read_csv('data/AIS_2023_01_01.csv', nrows=limit)
df_time = df_time.sort_values(by=['MMSI', 'BaseDateTime'])
df_time = df_time.groupby('MMSI').head(1)
df_time = df_time.reset_index(drop=True)

ship_data.to_csv('data/runetest.csv')
clusters = cluster.linkage_clustering(ship_data)

num_clusters = len(pd.Series(clusters).value_counts())
print(f"Number of clusters: {num_clusters}")

ship_data["cluster"] = clusters

ship_data.to_csv('data/runetest.csv')

collision.find_distance(ship_data, num_clusters)






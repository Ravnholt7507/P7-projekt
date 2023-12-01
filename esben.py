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
interpolated = df4.sort_values(by=['MMSI', 'BaseDateTime'])
interpolated = interpolated.drop_duplicates()
interpolated = interpolated.drop(columns=['Unnamed: 0'])
# Convert interpolated['BaseDateTime'] to seconds after midnight and rename column to time_seconds
interpolated['BaseDateTime'] = pd.to_datetime(interpolated['BaseDateTime'])
interpolated['BaseDateTime'] = interpolated['BaseDateTime'].dt.hour * 3600 + interpolated['BaseDateTime'].dt.minute * 60 + interpolated['BaseDateTime'].dt.second

df_time = pd.read_csv('data/AIS_2023_01_01.csv', nrows=limit)

# Sort by MMSI and BaseDateTime and only keep the first row for each MMSI where baseDateTime is the lowest
df_time = df_time.sort_values(by=['MMSI', 'BaseDateTime'])
df_time = df_time.drop_duplicates(subset=['MMSI'], keep='first')

# Convert df_time['BaseDateTime'] to seconds after midnight and rename column to time_seconds
df_time['BaseDateTime'] = pd.to_datetime(df_time['BaseDateTime'])
df_time['BaseDateTime'] = df_time['BaseDateTime'].dt.hour * 3600 + df_time['BaseDateTime'].dt.minute * 60 + df_time['BaseDateTime'].dt.second
df_time = df_time.rename(columns={'BaseDateTime': 'time_seconds'})

# Drop all columns except MMSI and time_seconds
df_time = df_time.drop(columns=['LAT','LON','SOG','COG'])
df_time.to_csv('data/time.csv')

# Merge df_time and interpolated
interpolated = pd.merge(interpolated, df_time, on='MMSI')
interpolated['sum_time'] = interpolated['BaseDateTime'] + interpolated['time_seconds']
interpolated['BaseDateTime'] = interpolated['sum_time']
interpolated = interpolated.drop(columns=['time_seconds', 'sum_time'])

# Sort by MMSI and BaseDateTime
interpolated = interpolated.sort_values(by=['MMSI', 'BaseDateTime'])

clusters = cluster.linkage_clustering(interpolated)

num_clusters = len(pd.Series(clusters).value_counts())
print(f"Number of clusters: {num_clusters}")

interpolated["cluster"] = clusters


collision.find_distance(interpolated, num_clusters)






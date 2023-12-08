import vector_based.cluster as cluster
import vector_based.collision as collision
import pandas as pd
import time

def round_time(x):
    return round(x, 2)

df2 = pd.read_csv('data/output.csv')
df3 = df2.groupby('MMSI').first().reset_index()
df4 = df2[df2['thresholdExceeded'] == True]
df4 = pd.concat([df3, df4])

interpolated = df4.sort_values(by=['MMSI', 'BaseDateTime'])
interpolated['BaseDateTime'] = pd.to_datetime(interpolated['BaseDateTime'])
interpolated['BaseDateTime'] = interpolated['BaseDateTime'].dt.hour * 3600 + interpolated['BaseDateTime'].dt.minute * 60 + interpolated['BaseDateTime'].dt.second

limit = 100000
# Read the data from another CSV file with a limit of 'limit' rows
df_time = pd.read_csv('data/AIS_2023_01_01.csv')
df_time = df_time.sort_values(by=['MMSI', 'BaseDateTime']).drop_duplicates(subset=['MMSI'], keep='first')

# Convert 'BaseDateTime' to seconds after midnight and rename the column to 'time_seconds'
df_time['BaseDateTime'] = pd.to_datetime(df_time['BaseDateTime'])
df_time['BaseDateTime'] = df_time['BaseDateTime'].dt.hour * 3600 + df_time['BaseDateTime'].dt.minute * 60 + df_time['BaseDateTime'].dt.second
df_time = df_time.rename(columns={'BaseDateTime': 'time_seconds'})
df_time = df_time.drop(columns=['LAT', 'LON', 'SOG', 'COG'])

interpolated = pd.merge(interpolated, df_time, on='MMSI')
interpolated['BaseDateTime'] = interpolated['BaseDateTime'] + interpolated['time_seconds']
interpolated = interpolated.drop(columns=['time_seconds'])
interpolated = interpolated.sort_values(by=['MMSI', 'BaseDateTime'])

# Perform clustering
start_time = time.time()
clusters = cluster.linkage_clustering(interpolated)
num_clusters = len(pd.Series(clusters).value_counts())
print(f"Number of clusters: {num_clusters}")
interpolated["cluster"] = clusters
# Drop columns that are not needed (Heading, Vessel Name, IMO, Call Sign, Vessel Type, Status, Length, Width, Draft, Cargo)
    # Check if Heading column exists
if 'Heading' in interpolated.columns:
    interpolated = interpolated.drop(columns=['Heading', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])

# interpolated.to_csv('data/colission_interpolated.csv', index=False)

# Print 5 largest clusters
print(interpolated['cluster'].value_counts().nlargest(5))

print(f"Clustering time: {round_time(time.time() - start_time)} seconds")

# Find distances between points in each cluster
start_time = time.time()
print("Finding distances...")

# If not vectorbased and COG is used, use this:
# collision.find_distance(interpolated, num_clusters)

# Take all rows where currentModel is COGbased and save them to a new dataframe
cogbased = interpolated[interpolated['currentModel'] == 'COGBasedModel']
# cogbased.to_csv('data/colission_cogbased.csv', index=False)

collision.find_vector_colission(cogbased, num_clusters)
print(f"Distance calculation time: {round_time(time.time() - start_time)} seconds")
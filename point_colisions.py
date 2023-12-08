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
df4 = df4.drop_duplicates(subset=['MMSI', 'BaseDateTime'], keep='first')
interpolated = df4.sort_values(by=['MMSI', 'BaseDateTime'])
print('lenght',len(interpolated))
# Perform clustering
start_time = time.time()
print('Clustering...')
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

# If not vectorbased and COG is used, use this:
# collision.find_distance(interpolated, num_clusters)

print('Calculating colisions...')
# Take all rows where currentModel is COGbased and save them to a new dataframe
cogbased = interpolated[interpolated['currentModel'] == 'COGBasedModel']

collision.find_vector_colission(cogbased, num_clusters)
print(f"Distance calculation time: {round_time(time.time() - start_time)} seconds")
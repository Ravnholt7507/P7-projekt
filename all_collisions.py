import vector_based.cleanse_all_collisions as cleanse
import vector_based.prediction as prediction
import vector_based.cluster as cluster
import vector_based.collision as collision
import pandas as pd
from haversine import haversine, Unit
import time

start_time = time.time()

def round_time(x):
    return round(x, 2)

print('Cleaning data...')
cleanse.cleanse('data/actual_positions.csv')

# Print time taken to run the program
print("in %s seconds" % (round_time(time.time() - start_time)))

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

df = pd.read_csv('data/actual_positions.csv')

print('Predicting ship positions...')
print(f"Number of ships: {len(df['MMSI'].unique())}")

prediction.all_ships(df)
print("in %s seconds" % (round_time(time.time() - start_time)))

# load ship data from a CSV file
ship_data = pd.read_csv('data/actual_positions.csv')
ship_data = ship_data.drop_duplicates(
    subset="MMSI", keep='first').reset_index(drop=True)

predictions = pd.read_csv('data/predictions.csv')
preds_lat = predictions['LAT']
preds_lon = predictions['LON']

ship_data["pred_lat"] = preds_lat
ship_data["pred_lon"] = preds_lon

# Calculate distance traveled for each ship
ship_data['distance'] = ship_data.apply(lambda row: haversine((row['LAT'], row['LON']), (row['pred_lat'], row['pred_lon']), unit=Unit.KILOMETERS), axis=1)

# Print boat data for the 10 boats that have traveled the furthest distance in km using the Haversine formula
sorted_ship_data = ship_data.sort_values(by='distance', ascending=False)
# print(sorted_ship_data[['MMSI', 'distance']].head(10),'km')

print('Clustering ships...')
# num_clusters = cluster.find_best_cluster(ship_data, 1000)
# clusters = cluster.cluster_ships_kmeans(ship_data, 1)
clusters = cluster.linkage_clustering(ship_data)
# print(clusters)

print("in %s seconds" % (round_time(time.time() - start_time)))

# Calculate number of clusters
num_clusters = len(pd.Series(clusters).value_counts())
print(f"Number of clusters: {num_clusters}")

ship_data["cluster"] = clusters

# Drop columns that are not needed (Heading, Vessel Name, IMO, Call Sign, Vessel Type, Status, Length, Width, Draft, Cargo
ship_data = ship_data.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign',
                           'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])

# Save ship data to CSV file
ship_data.to_csv('data/ship_data.csv', index=False)

collision.find_collisions(ship_data, num_clusters)

# Print time taken to run the program
print("--- Total %s seconds ---" % (round_time(time.time() - start_time)))
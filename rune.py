import matplotlib.pyplot as plt
import vector_based.prediction as prediction
import vector_based.cleanse_data as cleanse_data
import vector_based.cluster as cluster
import pandas as pd
import numpy as np

def find_intersection1(p1, v1, p2, v2):
    cross_product = np.cross(v1, v2)

    if np.allclose(cross_product, 0):
        print("Vectors are parallel or collinear, no intersection")
        # Vectors are parallel or collinear, no intersection
        return None

    t = np.cross(p2 - p1, v2) / cross_product
    s = np.cross(p2 - p1, v1) / cross_product

    if 0 <= t <= 1 and 0 <= s <= 1:
        intersection = p1 + t * v1
        return intersection
    else:
        # The vectors do not intersect within their segments
        return None

cleanse_data.cleanse()

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

prediction.all_ships()

# map.plot_land()

# collision.find_collisions()

# Use the following code to load ship data from a CSV file
ship_data = pd.read_csv('data/actual_positions.csv')
ship_data = ship_data.drop_duplicates(
    subset="MMSI", keep='first').reset_index(drop=True)

predictions = pd.read_csv('data/predictions.csv')
preds_lat = predictions['LAT']
preds_lon = predictions['LON']

ship_data["pred_lat"] = preds_lat
ship_data["pred_lon"] = preds_lon

clusters = cluster.cluster_ships_kmeans(ship_data, 3)

# Calculate number of clusters
num_clusters = len(pd.Series(clusters).value_counts())
print(f"Number of clusters: {num_clusters}")

ship_data["cluster"] = clusters

# Drop columns that are not needed (Heading, Vessel Name, IMO, Call Sign, Vessel Type, Status, Length, Width, Draft, Cargo
ship_data = ship_data.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign',
                           'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])


#Generate two new vectors wich intersect
p1 = np.array([1, 1])
v1 = np.array([4, 4])

p2 = np.array([2, 2])
v2 = np.array([5, 1])

# Add these vectors to the ship_data DataFrame
new_row1 = {'MMSI': 1, 'BaseDateTime': '2017-01-01T00:00:00', 'LAT': 34.0522, 'LON': -118.2437, 'SOG': 10,'COG':12, 'pred_lat':  37.7749, 'pred_lon': -122.4194, 'cluster': 0}
new_row2 = {'MMSI': 2, 'BaseDateTime': '2017-01-01T00:00:00', 'LAT': 36.7783, 'LON': -119.417, 'SOG': 10,'COG':12, 'pred_lat': 37.3541, 'pred_lon': -121.9552, 'cluster': 0}


new_row1 = pd.DataFrame([new_row1])
new_row2 = pd.DataFrame([new_row2])

# Concatenate the new row with your ship_data DataFrame
ship_data = pd.concat([ship_data, new_row1], ignore_index=True)
ship_data = pd.concat([ship_data, new_row2], ignore_index=True)

print(ship_data)

# Make function where intersection is found for each point p1 to every point p2 in the same cluster
for cluster in range(num_clusters):
    cluster_data = ship_data[ship_data['cluster'] == cluster]
    cluster_data = cluster_data.reset_index(drop=True)

    # Print which cluster is being checked
    print(f"Cluster: {cluster}")

    p1 = (cluster_data['LON'].tolist(), cluster_data['LAT'].tolist())
    v1 = (cluster_data['pred_lon'].tolist(), cluster_data['pred_lat'].tolist())

    # Make loop where intersection is found for each p1 and v1 to every point p2 and v2 in the same cluster
    for x in range(len(p1[0])-1):
        for y in range(x+1, len(p1[0])):
            intersection = find_intersection1(np.array([p1[0][x], p1[1][x]]),
                                              np.array([v1[0][x]-p1[0][x], v1[1][x] - p1[1][x]]),
                                              np.array([p1[0][y], p1[1][y]]),
                                              np.array([v1[0][y]-p1[0][y], v1[1][y] - p1[1][y]]))

            if intersection is not None:
                # Reverse order of intersection to Lat, Lon
                intersection = (intersection[1], intersection[0])
                print(f"Intersection point: {intersection}")
            else:
                print("The vectors do not intersect.")
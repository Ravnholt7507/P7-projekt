import matplotlib.pyplot as plt
import vector_based.cleanse_all_collisions as cleanse
import vector_based.prediction as prediction
import vector_based.cluster as cluster
import pandas as pd
import numpy as np
from haversine import haversine, Unit

def find_intersection(p1, v1, p2, v2):
    cross_product = np.cross(v1, v2)

    if np.allclose(cross_product, 0):
        # print("Vectors are parallel or collinear, no intersection")
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

print('Cleaning data...')
cleanse.cleanse('data/actual_positions.csv')

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

df = pd.read_csv('data/actual_positions.csv')

print('Predicting ship positions...')
prediction.all_ships(df)

# Use the following code to load ship data from a CSV file
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
print(sorted_ship_data[['MMSI', 'distance']].head(10),'km')

print('Clustering ships...')
# num_clusters = cluster.find_best_cluster(ship_data, 1000)
clusters = cluster.cluster_ships_kmeans(ship_data, 30)
# clusters = cluster.linkage_clustering(ship_data)
# print(clusters)

# Calculate number of clusters
num_clusters = len(pd.Series(clusters).value_counts())
print(f"Number of clusters: {num_clusters}")

ship_data["cluster"] = clusters

# Drop columns that are not needed (Heading, Vessel Name, IMO, Call Sign, Vessel Type, Status, Length, Width, Draft, Cargo
ship_data = ship_data.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign',
                           'VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])

# Save ship data to CSV file
ship_data.to_csv('data/ship_data.csv', index=False)

Total_intersections = 0
max_intersection_count = 0
max_cluster = 0
# Make function where intersection is found for each point p1 to every point p2 in the same cluster
print('Finding intersections...')
for cluster in range(num_clusters):
    cluster_data = ship_data[ship_data['cluster'] == cluster]
    cluster_data = cluster_data.reset_index(drop=True)

    # Print which cluster is being checked
    print(f"Cluster: {cluster}")

    p1 = (cluster_data['LON'].tolist(), cluster_data['LAT'].tolist())
    v1 = (cluster_data['pred_lon'].tolist(), cluster_data['pred_lat'].tolist())
    intersection_count = 0
    # Make loop where intersection is found for each p1 and v1 to every point p2 and v2 in the same cluster
    for x in range(len(p1[0])-1):
        for y in range(x+1, len(p1[0])):
            intersection = find_intersection(np.array([p1[0][x], p1[1][x]]),
                                              np.array([v1[0][x]-p1[0][x], v1[1][x] - p1[1][x]]),
                                              np.array([p1[0][y], p1[1][y]]),
                                              np.array([v1[0][y]-p1[0][y], v1[1][y] - p1[1][y]]))

            if intersection is not None:
                """
                # Add legend LON and LAT
                plt.xlabel('LON')
                plt.ylabel('LAT')
         
                # plot p1 and p2
                plt.scatter(p1[0][x], p1[1][x], color='red')
                plt.scatter(p1[0][y], p1[1][y], color='red')
                # Plot the intersection points
                plt.scatter(*intersection, color='black')
                #plot v1 and v2
                plt.scatter(v1[0][x], v1[1][x], color='blue')
                plt.scatter(v1[0][y], v1[1][y], color='blue')
                
                # Plot the vectors between p1 and v1
                plt.plot([p1[0][x], v1[0][x]], [p1[1][x], v1[1][x]], color='blue')
                plt.plot([p1[0][y], v1[0][y]], [p1[1][y], v1[1][y]], color='blue')
                
                plt.show()
                
                # Reverse intersection array
                # intersection = intersection[::-1]
                # print(f"Intersection point: {intersection}")
                """
                intersection_count += 1
            # else:
                # print("The vectors do not intersect.")
                # Save the cluster with the most intersections
        
    Total_intersections += intersection_count
        
    print(f"Intersection count: {intersection_count}")
    # Find the cluster with the most intersections
    if intersection_count > max_intersection_count:
        max_intersection_count = intersection_count
        max_cluster = cluster


print(f"Cluster with the most intersections: {max_cluster}")
print(f"Intersection count: {max_intersection_count}")
print(f"Total intersections: {Total_intersections}")

# Plot all the points in cluster 
cluster_data = ship_data[ship_data['cluster'] == max_cluster]
cluster_data = cluster_data.reset_index(drop=True)
# print(cluster_data)
plt.scatter(cluster_data['LON'], cluster_data['LAT'], color='red')
plt.scatter(cluster_data['pred_lon'], cluster_data['pred_lat'], color='blue')
# Plot lines between p1 and v1
for i in range(len(cluster_data['LON'])):
    plt.plot([cluster_data['LON'][i], cluster_data['pred_lon'][i]], [cluster_data['LAT'][i], cluster_data['pred_lat'][i]], color='blue')

# Plot the intersection points
if intersection is not None:
    plt.scatter(*intersection, color='black')

plt.show()
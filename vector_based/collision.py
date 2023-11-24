import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

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

# Make another find_collisions function but using tqdm
def find_collisions(ship_data, num_clusters):
    
    # Clear intersection_points.csv
    with open('data/intersection_points.csv', 'w') as fp:
        fp.truncate()
        # Write header
        fp.write('LON,LAT,cluster,id,time_diff\n')
    
    Total_intersections = 0
    max_intersection_count = 0
    max_cluster = 0
    
    # Make function where intersection is found for each point p1 to every point p2 in the same cluster
    print('Finding intersections...')
    for cluster in tqdm(range(num_clusters)):

        cluster_data = ship_data[ship_data['cluster'] == cluster]
        cluster_data = cluster_data.reset_index(drop=True)

        p1 = (cluster_data['LON'].tolist(), cluster_data['LAT'].tolist())
        v1 = (cluster_data['pred_lon'].tolist(), cluster_data['pred_lat'].tolist())
        intersection_count = 0
        time_intersection = 0

        for x in range(len(p1[0])):
            for y in range(x+1, len(p1[0])):
                if cluster_data['MMSI'].iloc[x] != cluster_data['MMSI'].iloc[y]:
                    intersection = find_intersection(np.array([p1[0][x], p1[1][x]]),
                                                    np.array([v1[0][x]-p1[0][x], v1[1][x] - p1[1][x]]),
                                                    np.array([p1[0][y], p1[1][y]]),
                                                    np.array([v1[0][y]-p1[0][y], v1[1][y] - p1[1][y]]))

                    if intersection is not None:
                        
                        # Save intersection points and clusters and time diff between the two ships to a csv file
                        # Convert 'BaseDateTime' to datetime format
                        cluster_data['BaseDateTime'] = pd.to_datetime(cluster_data['BaseDateTime'])
                        time_diff = abs(cluster_data['BaseDateTime'][x] - cluster_data['BaseDateTime'][y])

                        # Check if the time difference between the two ships is less than 3 minutes
                        if abs(cluster_data['BaseDateTime'][x] - cluster_data['BaseDateTime'][y]) < pd.Timedelta(minutes=3):
                            time_intersection += 1
                            
                            with open('data/intersection_points.csv', 'a') as fp:
                                fp.write(f"{intersection[0]},{intersection[1]},{cluster},{1},{time_diff}\n")
                            
                            # print(f"Ship 1: {cluster_data['MMSI'][x]}")
                            # print(f"Ship 2: {cluster_data['MMSI'][y]}")
                            # print(f"Time of ship 1: {cluster_data['BaseDateTime'][x]}")
                            # print(f"Time of ship 2: {cluster_data['BaseDateTime'][y]}")
                        else:
                            # print(f"Time difference between ship 1 and ship 2 is more than 3 minutes")
                            intersection_count += 1
                            
                            with open('data/intersection_points.csv', 'a') as fp:
                                fp.write(f"{intersection[0]},{intersection[1]},{cluster},{0},{time_diff}\n")
                                

        Total_intersections += intersection_count
        
        # Find the cluster with the most intersections
        if time_intersection > max_intersection_count:
            max_intersection_count = time_intersection
            max_cluster = cluster

    print(f"Total intersections: {Total_intersections}")
    print(f"Cluster with the most intersections: Cluster - {max_cluster}")
    print(f"Intersections in cluster {max_cluster}: {max_intersection_count}, where the time difference is less than 3 minutes")

    # Plot all the points in cluster 
    cluster_data = ship_data[ship_data['cluster'] == max_cluster]
    cluster_data = cluster_data.reset_index(drop=True)
    plt.scatter(cluster_data['LON'], cluster_data['LAT'], color='red')
    plt.scatter(cluster_data['pred_lon'], cluster_data['pred_lat'], color='green')

    # Plot points from intersection_points.csv where the last column is 0
    intersection_points = pd.read_csv('data/intersection_points.csv')
    intersection_points = intersection_points[intersection_points['cluster'] == max_cluster]
    intersection_points = intersection_points[intersection_points['id'] == 0]
    plt.scatter(intersection_points['LON'], intersection_points['LAT'], color='purple')
    
    # Plot points from intersection_points.csv where the last column is 1
    intersection_points = pd.read_csv('data/intersection_points.csv')
    intersection_points = intersection_points[intersection_points['cluster'] == max_cluster]
    intersection_points = intersection_points[intersection_points['id'] == 1]
    plt.scatter(intersection_points['LON'], intersection_points['LAT'], color='yellow')
    
    # Make background lightblue
    plt.gca().set_facecolor('lightblue')
    
    # Add legend LON and LAT
    plt.xlabel('LON')
    plt.ylabel('LAT')
    
    # Plot lines between p1 and v1
    for i in range(len(cluster_data['LON'])):
        plt.plot([cluster_data['LON'][i], cluster_data['pred_lon'][i]], [cluster_data['LAT'][i], cluster_data['pred_lat'][i]], color='green')
    plt.title(f"Cluster {max_cluster} - {max_intersection_count} intersections")
    plt.show()
    plt.savefig(f"figures/cluster_{max_cluster}_intersections.png")
    
    return max_cluster

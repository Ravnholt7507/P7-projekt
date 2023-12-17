import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from haversine import haversine, Unit
from tqdm import tqdm
from math import asin, atan2, cos, degrees, radians, sin
from shapely.geometry import Point
from shapely.geometry import LineString
from geographiclib.geodesic import Geodesic

def find_intersection(p1, v1, p2, v2):
    cross_product = np.cross(v1, v2)

    if np.allclose(cross_product, 0):
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
    
def find_collisions(ship_data, num_clusters):
    
    with open('data/intersection_points.csv', 'w') as fp:
        fp.truncate()
        fp.write('LON,LAT,cluster,id,time_diff\n')
    
    Total_intersections = 0
    max_intersection_count = 0
    max_cluster = 0
    
    # Intersection is found for each point p1 to every point p2 in the same cluster
    print('Finding intersections...')
    for cluster in tqdm(range(num_clusters)):

        cluster_data = ship_data[ship_data['cluster'] == cluster]
        cluster_data = cluster_data.reset_index(drop=True)

        p1 = (cluster_data['LON'].tolist(), cluster_data['LAT'].tolist())
        v1 = (cluster_data['predictedLON'].tolist(), cluster_data['predictedLAT'].tolist())
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
                        else:
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
    plt.scatter(cluster_data['predictedLON'], cluster_data['predictedLAT'], color='green')

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
    plt.xlabel('LON')
    plt.ylabel('LAT')
    
    # Plot lines between p1 and v1
    for i in range(len(cluster_data['LON'])):
        plt.plot([cluster_data['LON'][i], cluster_data['predictedLON'][i]], [cluster_data['LAT'][i], cluster_data['predictedLAT'][i]], color='green')
    plt.title(f"Cluster {max_cluster} - {max_intersection_count} intersections")
    plt.show()
    plt.savefig(f"figures/cluster_{max_cluster}_intersections.png")
    
    return max_cluster

def find_vector_colission(ship_data, num_clusters):
    collisions = 0
    
    with open('data/vector_colissions.csv', 'w') as fp:
        fp.truncate()
        fp.write('MMSI1,Pos1,vec1,time1,MMSI2,pos2,vec2,time2,intersection,time_diff\n')
        
    for cluster in tqdm(range(num_clusters)):
        cluster_data = ship_data[ship_data['cluster'] == cluster]
        cluster_data = cluster_data.reset_index(drop=True)
        cluster_data['BaseDateTime'] = pd.to_datetime(cluster_data['BaseDateTime'])

        p1 = np.array([cluster_data['LON'], cluster_data['LAT']])
        vector = np.array([cluster_data['LON'], cluster_data['LAT'], cluster_data['SOG'], cluster_data['COG']])

        v1 = vectors(vector)
        v1 = np.array(v1)
        
        # Compare every vector with every other vector in the same cluster
        for x in range(len(p1[0])):
            for y in range(x+1, len(p1[0])):
                if cluster_data['MMSI'].iloc[x] != cluster_data['MMSI'].iloc[y]:
                    pos1 = p1[:,x]
                    pos2 = p1[:,y]
                    vec1 = v1[x,:] - p1[:,x]
                    vec2 = v1[y,:] - p1[:,y]
                    
                    intersection = find_intersection(pos1, vec1, pos2, vec2)
                    
                    if intersection is not None:
                        collisions += 1
                        time_diff = abs(cluster_data['BaseDateTime'][x] - cluster_data['BaseDateTime'][y])

                        with open('data/vector_colissions.csv', 'a') as fp:
                            fp.write(f"{cluster_data['MMSI'].iloc[x]},{pos1},{vec1},{cluster_data['BaseDateTime'][x]},{cluster_data['MMSI'].iloc[y]},{pos2},{vec2},{cluster_data['BaseDateTime'][y]},{intersection},{time_diff}\n")
    
    print(collisions)

def vectors(vector):
    v1 = []
    for i in range(len(vector[0])):
        speed = vector[2][i] * 1.852
        distance = speed * 600 / 3600
        bearing = vector[3][i]
        v1.append(get_point_at_distance(vector[1][i], vector[0][i], distance, bearing))
    return v1

def find_intersection_between_all(ship_data, num_clusters):

    arb_time = 600
    count = 0
    checks = 0

    for cluster in tqdm(range(num_clusters)):
        cluster_data = ship_data[ship_data['cluster'] == cluster]
        cluster_data = cluster_data.reset_index(drop=True)
        cluster_data['BaseDateTime'] = pd.to_datetime(cluster_data['BaseDateTime'])

        circles = cluster_data[cluster_data["currentModel"] == "pointBasedModel"]
        vectors = cluster_data[cluster_data["currentModel"] != "pointBasedModel"]
        
        points = np.array([circles['LON'], circles['LAT'], circles['radiusThreshold']])
        lines = np.array([vectors['LON'], vectors['LAT'], vectors['predictedLON'], vectors['predictedLAT'], vectors['SOG']])
        print('x', len(points[0]))
        print('y', len(lines[0]))
        print('circles', len(circles))
        print('vectors', len(vectors))
        for x in range(len(points[0])):
            for y in range(len(lines[0])):
                LON, LAT = lines[0][y], lines [1][y]
                PREDLON, PREDLAT = lines[2][y], lines[3][y]
                
                distance = lines[4][y] * arb_time / 3600
                COG = Geodesic.WGS84.Inverse(LAT, LON, PREDLAT, PREDLON)

                updated_cords = get_point_at_distance(LAT, LON, distance, COG['azi1'])

                line = LineString([(LON, LAT), updated_cords])
                center = points[0][x], points[1][x]
                radius = points[2][x]

                count += find_line_circle_intersection(center, radius, line)
                checks += 1
                
    print(count)
    print(checks)

def find_line_circle_intersection(p, r, line):

    center_point = Point(p)
    circle_boundary = center_point.buffer(r).boundary

    intersection_points = circle_boundary.intersection(line)

    if intersection_points.is_empty:
        return 0
    else:
        return 1

def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
    '''
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    '''
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(sin(a) * sin(d/R) * cos(lat1), cos(d/R) - sin(lat1) * sin(lat2))
    return [degrees(lon2), degrees(lat2)]

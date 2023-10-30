import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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

def find_collisions():
    
    df = pd.read_csv("data/boats_hh.csv")
    prediction = pd.read_csv("data/predictions_hh.csv")

    MMSI = prediction['MMSI'].unique()
    Actual_ship1 = df[df['MMSI'] == MMSI[0]]
    print(MMSI[0])
    prediction1 = prediction[prediction['MMSI'] == MMSI[0]]

    Actual_ship2 = df[df['MMSI'] == MMSI[1]]
    prediction2 = prediction[prediction['MMSI'] == MMSI[1]]

    p1 = (Actual_ship1['LON'].tolist(), Actual_ship1['LAT'].tolist())
    v1 = (prediction1['LON'].tolist(), prediction1['LAT'].tolist())
    # Remove the first element of the list
    p1 = (p1[0][1:], p1[1][1:])

    p2 = (Actual_ship2['LON'].tolist(), Actual_ship2['LAT'].tolist())
    v2 = (prediction2['LON'].tolist(), prediction2['LAT'].tolist())
    # Remove the first element of the list
    p2 = (p2[0][1:], p2[1][1:])

    plt.figure()
    
    # Make loop where intersection is found for each point p1 to every point p2
    for x in range(len(p1[0])-1):
        for y in range(len(p2[0])-1):
            intersection = find_intersection(np.array([p1[0][x], p1[1][x]]), 
                                             np.array([v1[0][x+1]-p1[0][x], v1[1][x+1] - p1[1][x]]),
                                             np.array([p2[0][y], p2[1][y]]),
                                             np.array([v2[0][y+1]-p2[0][y], v2[1][y+1] - p2[1][y]]))

            if intersection is not None:
                print(f"Intersection point: {intersection}")
                # Plot the intersection points
                plt.scatter(*intersection, color='black')
            else:
                print("The vectors do not intersect.")

    # Plot the vectors
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.plot(p1[0], p1[1], 'red', marker='.', label='Actual', linestyle='None')
    plt.plot(v1[0], v1[1], 'blue', marker='.',
             label='Predicted', linestyle='None')
    plt.plot(p2[0], p2[1], 'red', marker='.', label='Actual', linestyle='None')
    plt.plot(v2[0], v2[1], 'blue', marker='.',
             label='Predicted', linestyle='None')

    # Draw arrwos from actual to predicted
    for x in range(len(p1[0])-1):
        plt.arrow(p1[0][x], p1[1][x], v1[0][x+1]-p1[0][x], v1[1][x+1] - p1[1][x],
                  color='green', width=0.00001, head_width=0.00005, length_includes_head=True)

    for x in range(len(p2[0])-1):
        plt.arrow(p2[0][x], p2[1][x], v2[0][x+1]-p2[0][x], v2[1][x+1] - p2[1][x],
                  color='green', width=0.00001, head_width=0.00005, length_includes_head=True)

    plt.show()

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import pandas as pd


def cluster_ships_knn(ship_data, num_clusters, k_neighbors=3):
    """
    Cluster ships based on latitude and longitude using KNN.

    Parameters:
        - ship_data: A 2D NumPy array or Pandas DataFrame with columns 'lat' and 'lon'.
        - num_clusters: The number of clusters to create.
        - k_neighbors: The number of nearest neighbors to consider.

    Returns:
        - None
    """
    # Ensure ship_data is a DataFrame
    if not isinstance(ship_data, pd.DataFrame):
        ship_data = pd.DataFrame(ship_data, columns=['LAT', 'LON'])

    # Extract latitude and longitude as a NumPy array
    coordinates = ship_data.iloc[:, 2:4].to_numpy()

    # Fit KNN model to the data
    knn = NearestNeighbors(n_neighbors=k_neighbors)
    knn.fit(coordinates)

    # Compute the nearest neighbors for each data point
    distances, indices = knn.kneighbors(coordinates)

    # Calculate cluster labels based on the majority class of the k-nearest neighbors
    cluster_labels = np.zeros(len(ship_data))
    for i in range(len(ship_data)):
        cluster_labels[i] = np.argmax(np.bincount(indices[i]))

    #print number of ships in each cluster
    print("Number of ships in each cluster:")
    print(pd.Series(cluster_labels).value_counts())
    
    #print number of clusters
    print("Number of clusters:")
    print(len(pd.Series(cluster_labels).value_counts()))
    
    # Create a scatter plot to visualize ship clusters
    plt.figure(figsize=(10, 8))
    plt.scatter(ship_data['LON'], ship_data['LAT'], c=cluster_labels, cmap='rainbow', marker='o', s=50)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Ship Clusters (KNN)')
    plt.show()

def cluster_ships_kmeans(ship_data, num_clusters):
    """
    Visualize ship clusters based on latitude and longitude.

    Parameters:
        - ship_data: A 2D NumPy array or Pandas DataFrame with columns 'lat' and 'lon'.
        - num_clusters: The number of clusters to create.

    Returns:
        - None
    """
    # Ensure ship_data is a DataFrame
    if not isinstance(ship_data, pd.DataFrame):
        ship_data = pd.DataFrame(ship_data, columns=['LAT', 'LON'])
    
    # Extract latitude and longitude from csv as a NumPy array
    coordinates = ship_data.iloc[:, 2:4].to_numpy()
    
    # Initialize and fit the K-Means model
    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10)
    cluster_labels = kmeans.fit_predict(coordinates)

    # Get cluster centers
    cluster_centers = kmeans.cluster_centers_

    #print number of clusters
    print("Number of clusters:")
    print(len(pd.Series(cluster_labels).value_counts()))
    
    #print number of ships in each cluster
    print("Number of ships in each cluster:")
    print(pd.Series(cluster_labels).value_counts())


    # Create a scatter plot to visualize ship clusters
    # plt.figure(figsize=(10, 8))
    
    # plt.scatter(ship_data['LON'], ship_data['LAT'],
    #             c=cluster_labels, cmap='rainbow', marker='o', s=50)
    # plt.scatter(cluster_centers[:, 1], cluster_centers[:, 0],
    #             c='black', marker='x', s=100, label='Cluster Centers')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # plt.title('Ship Clusters')
    # plt.legend()
    # plt.show()
    
    return cluster_labels

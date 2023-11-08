import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.cluster.hierarchy import fcluster
import cartopy.crs as ccrs

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

    merge_pairs = []

    # Check if clusters are close to each other
    for i in range(num_clusters):
        for j in range(i+1, num_clusters):
            distance = np.sqrt((cluster_centers[i][0] - cluster_centers[j][0])**2 + (cluster_centers[i][1] - cluster_centers[j][1])**2)
            if distance < 0.5:
                # print(f"Clusters {i} and {j} are close to each other.")
                # print(f"Distance between cluster centers: {distance}")
                merge_pairs.append(j)

    # Merge clusters
    for j in set(merge_pairs):
        cluster_labels = np.where(cluster_labels == j, merge_pairs[0], cluster_labels)

    print("Number of ships in each cluster after merging:")
    print(pd.Series(cluster_labels).value_counts())
    
    # Create a new list of cluster centers
    new_cluster_centers = [center for i, center in enumerate(cluster_centers) if i not in set(merge_pairs)]
    cluster_centers = np.array(new_cluster_centers)
    
    print(cluster_centers)
    
    # Create a scatter plot to visualize ship clusters
    plt.figure(figsize=(10, 8))
    plt.scatter(ship_data['LON'], ship_data['LAT'], c=cluster_labels, cmap='rainbow', marker='o', s=50)
    plt.scatter(cluster_centers[:, 1], cluster_centers[:, 0], c='black', marker='x', s=100) # swap the order of the coordinates
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Ship Clusters (K-Means)')
    plt.show()
    
    
    return cluster_labels

# Function to find best number of clusters
def find_best_cluster(ship_data, max_clusters):
    """
    Find the best number of clusters for a dataset.

    Parameters:
        - ship_data: A 2D NumPy array or Pandas DataFrame with columns 'lat' and 'lon'.
        - max_clusters: The maximum number of clusters to try.

    Returns:
        - None
    """
    # Ensure ship_data is a DataFrame
    if not isinstance(ship_data, pd.DataFrame):
        ship_data = pd.DataFrame(ship_data, columns=['LAT', 'LON'])

    # Extract latitude and longitude as a NumPy array
    coordinates = ship_data.iloc[:, 2:4].to_numpy()

    # Initialize and fit the K-Means model
    kmeans = KMeans(n_clusters=max_clusters, random_state=0, n_init=10)
    kmeans.fit(coordinates)

    # Calculate the sum of squared distances for each cluster label
    sse = []
    for i in range(1, max_clusters+1):
        kmeans = KMeans(n_clusters=i, random_state=0, n_init=10)
        kmeans.fit(coordinates)
        sse.append(kmeans.inertia_)

    # Plot the sum of squared distances for each cluster label
    plt.figure(figsize=(10, 8))
    plt.plot(range(1, max_clusters+1), sse, marker='o')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Sum of Squared Distances')
    plt.title('Elbow Method')
    plt.show()
    
    # Print the best number of clusters
    print(f"Best number of clusters: {np.argmin(sse)+1}")
    
    # Return the best number of clusters
    return np.argmin(sse)+1


# Linkage clustering
def linkage_clustering(ship_data):
    
    # Extract relevant columns as a NumPy array
    coordinates = ship_data[['LAT', 'LON']].to_numpy()

    linkage_matrix = linkage(coordinates, method='average', metric='euclidean')
    dendrogram(linkage_matrix)
    
    import cartopy.crs as ccrs

    plt.show()

    # Specify the threshold or number of clusters
    threshold = 2.0
    clusters = fcluster(linkage_matrix, threshold, criterion='distance')

    # Add clusters to ship_data as a new column
    ship_data['cluster'] = clusters

    print(clusters)

    # Assuming 'ship_data' is a DataFrame with columns 'LAT', 'LON', and 'cluster'
    cluster_stats = ship_data.groupby('cluster').agg({
        'LAT': ['mean', 'std', 'count'],
        'LON': ['mean', 'std']
    })

    print(cluster_stats)

    # Assuming you have a DataFrame 'ship_data' with 'LAT', 'LON', and 'cluster' columns
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

    for cluster_id, cluster_data in ship_data.groupby('cluster'):
        ax.scatter(cluster_data['LON'], cluster_data['LAT'], label=f'Cluster {cluster_id}')

    ax.coastlines()
    ax.legend()
    plt.show()
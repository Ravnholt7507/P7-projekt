import vector_based.prediction as prediction
import vector_based.cleanse_data as cleanse_data
import vector_based.collision as collision
import vector_based.map as map
import vector_based.cluster as cluster
import pandas as pd

cleanse_data.cleanse()

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

prediction.all_ships()

map.plot_land()

collision.find_collisions()

# Use the following code to load ship data from a CSV file
ship_data = pd.read_csv('data/1_boats.csv')
cluster.cluster_ships_kmeans(ship_data, 3)
# cluster.cluster_ships_knn(ship_data, 2)
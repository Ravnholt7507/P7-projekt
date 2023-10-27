import vector_based.prediction as prediction

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

prediction.all_ships()
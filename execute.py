import vector_based.prediction as prediction
import vector_based.cleanse_data as cleanse
#cleanse.cleanse()
prediction.predict_intv()

with open('data/predictions.csv', 'w') as fp:
    fp.truncate()

prediction.all_ships()
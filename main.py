import vector_based.prediction as prediction
import pandas as pd

df = pd.read_csv('data/boats.csv')

prediction.predict_intv(df)

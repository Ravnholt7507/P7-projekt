import plotly.express as px
import pandas as pd

df = pd.read_csv("boats.csv")

fig = px.scatter_geo(df,lat='LAT',lon='LON', hover_name="MMSI")
fig.update_layout(title = 'World map', title_x=0.5)
fig.show()
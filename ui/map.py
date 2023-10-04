import plotly.express as px
import pandas as pd

df = pd.read_csv("boats.csv")

fig = px.scatter_geo(df,lat='LAT',lon='LON',hover_data='BaseDateTime', hover_name="MMSI",color_discrete_sequence=["red"])
fig.update_geos(
    scope="north america",
    resolution = 110, # Set to 50 or 110
    showlakes=True, lakecolor="Blue",
    showrivers=True, rivercolor="Blue"
)

fig.update_layout(title = 'North America', title_x=0.5)
fig.show()
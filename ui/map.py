import plotly.express as px
import pandas as pd

df = pd.read_csv("boats.csv")

# id = df[(df.groupby('MMSI').size())]
id = df.groupby('MMSI').filter(lambda x: len(x) > 10)

print(id)

fig = px.scatter_geo(id,lat='LAT',lon='LON', hover_name="BaseDateTime")
fig.update_geos(
    scope="north america",
    resolution = 110, # Set to 50 or 110
    showlakes=True, lakecolor="Blue",
    showrivers=True, rivercolor="Blue"
)

fig.update_layout(title = 'North America', title_x=0.5)
# fig.show()
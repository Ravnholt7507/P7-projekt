import plotly.express as px
import pandas as pd

df = pd.read_csv("boats.csv")

fig = px.scatter_geo(df, lat='LAT', lon='LON', hover_data=['BaseDateTime','COG','Heading'],
                     hover_name="MMSI", color_discrete_sequence=["red"])
fig.update_geos(
    scope="north america",
    resolution=110,  # Set to 50 or 110
    showlakes=True, lakecolor="Blue",
    showrivers=True, rivercolor="Blue"
)

# plot only two coordinates for testing in green color
#COG
LAT = 24.49526005
LON = -79.86377995

#Heading
LAT2 = 24.49891825
LON2 = -79.86012175

fig.add_trace(px.scatter_geo(lat=[LAT], lon=[
              LON], color_discrete_sequence=["green"]).data[0])

fig.add_trace(px.scatter_geo(lat=[LAT2], lon=[
              LON2], color_discrete_sequence=["blue"]).data[0])

fig.update_layout(title='North America', title_x=0.5)
fig.show()

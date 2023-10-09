import plotly.express as px
import pandas as pd

def plot():
    df = pd.read_csv("boats.csv")

    fig = px.scatter_geo(df, lat='LAT', lon='LON', hover_data=['BaseDateTime','COG','Heading'],
                        hover_name="MMSI", color_discrete_sequence=["red"])
    fig.update_geos(
        scope="north america",
        resolution=110,  # Set to 50 or 110
        showlakes=True, lakecolor="Blue",
        showrivers=True, rivercolor="Blue"
    )

    df2 = pd.read_csv("predictions.csv")

    fig.add_trace(px.scatter_geo(df2,lat='LAT', lon='LON',hover_name="MMSI", color_discrete_sequence=["green"]).data[0])

    fig.update_layout(title='North America', title_x=0.5)
    fig.show()

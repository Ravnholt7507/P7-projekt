import plotly.express as px
import pandas as pd


def plot():
    df = pd.read_csv('data/boats.csv')

    fig = px.scatter_geo(df, lat='LAT', lon='LON', hover_data=['BaseDateTime', 'SOG', 'COG', 'Heading'],
                         hover_name='MMSI', color_discrete_sequence=['red'])
    fig.update_geos(
        scope='north america',
        resolution=110,  # Set to 50 or 110
        showlakes=True, lakecolor='Blue',
        showrivers=True, rivercolor='Blue'
    )

    df2 = pd.read_csv('data/predictions.csv')

    fig.add_trace(px.scatter_geo(df2, lat='LAT', lon='LON', hover_data=[
                  'BaseDateTime', 'SOG'], hover_name='MMSI', color_discrete_sequence=['green']).data[0])

    fig.update_layout(title='North America', title_x=0.5)
    #fig.show()
    fig.write_html('Figures/first_figure.html', auto_open=False)

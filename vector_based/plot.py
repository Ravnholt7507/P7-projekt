import matplotlib.pyplot as plt
import pandas as pd
import pickle
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature

def plot():
    df = pd.read_csv("data/boats.csv")
    prediction = pd.read_csv("data/predictions.csv")

    MMSI = prediction['MMSI'].unique()
    Actual_ship = df[df['MMSI'] == MMSI[0]]

    act_lats = Actual_ship['LAT'].tolist()
    act_lons = Actual_ship['LON'].tolist()
    pred_lats = prediction['LAT'].tolist()
    pred_lons = prediction['LON'].tolist()

    fig = plt.figure(1)
    plt.subplot()
    plt.title('Actual vs Predicted ship path')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.plot(act_lons, act_lats, 'red', marker='.', label='Actual')
    plt.plot(pred_lons, pred_lats, 'blue', marker='.', label='Predicted')
    plt.legend(loc='upper right')

    for x in range(len(act_lats)-1):
        plt.arrow(act_lons[x], act_lats[x], act_lons[x+1]-act_lons[x], act_lats[x+1] -
                  act_lats[x], color='red', width=0.00001, head_width=0.00005, length_includes_head=True)
    for x in range(len(pred_lats)-1):
        plt.arrow(pred_lons[x], pred_lats[x], pred_lons[x+1]-pred_lons[x], pred_lats[x+1] -
                  pred_lats[x], color='blue', width=0.00001, head_width=0.00005, length_includes_head=True)
    plt.tight_layout()
    # plt.show()
    plt.savefig('Figures/actVsPred.png')
    with open('Figures/actVsPred.obj', 'wb') as f:
        pickle.dump(fig, f)
    plt.close()

def actualToPred():
    df = pd.read_csv("data/boats.csv")
    prediction = pd.read_csv("data/predictions.csv")

    MMSI = prediction['MMSI'].unique()
    Actual_ship = df[df['MMSI'] == MMSI[0]]

    act_lats = Actual_ship['LAT'].tolist()
    act_lons = Actual_ship['LON'].tolist()
    pred_lats = prediction['LAT'].tolist()
    pred_lons = prediction['LON'].tolist()

    fig = plt.figure(1)
    plt.subplot()
    plt.title('Actual to Predicted ship path')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.plot(act_lons, act_lats, 'red', marker='.', label='Actual', linestyle='None')
    plt.plot(pred_lons, pred_lats, 'blue', marker='.', label='Predicted', linestyle='None')
    plt.legend(loc='upper right')
    
    for x in range(len(act_lats)-1):
        plt.arrow(act_lons[x], act_lats[x], pred_lons[x]-act_lons[x], pred_lats[x] - act_lats[x], color='green', width=0.000001, head_width=0.0002, length_includes_head=True)
        #arrow with head in the middle of the line between two points
        #plt.arrow(act_lons[x], act_lats[x], (pred_lons[x]-act_lons[x])/2, (pred_lats[x] - act_lats[x])/2, color='green', width=0.000001, head_width=0.00003, length_includes_head=True)
    plt.tight_layout()
    plt.savefig('Figures/predPlotArrows.png')
    with open('Figures/predPlotArrows.obj', 'wb') as f:
        pickle.dump(fig, f)
    plt.close()

def worldMapPlot():
    ccrs.PlateCarree()
    plt.axes(projection=ccrs.PlateCarree())

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.LAND, edgecolor='black')
    ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
    ax.add_feature(cartopy.feature.RIVERS)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, color = 'None')
    df = pd.read_csv("data/boats.csv")
    plt.scatter(df['LON'], df['LAT'], s=0.1, c='red', marker='*', transform=ccrs.PlateCarree())
    plt.tight_layout()
    plt.savefig('Figures/map.png')
    with open('Figures/map.obj', 'wb') as f:
        pickle.dump(fig, f)
    plt.close()

def Load_plot(pltName):
    fig = plt.figure(1)
    plt.subplot()
    with open(pltName, 'rb') as file:
        fig = pickle.load(file)
    return fig

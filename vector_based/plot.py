import matplotlib.pyplot as plt
import pandas as pd


def plot():
    df = pd.read_csv("boats.csv")
    prediction = pd.read_csv("predictions.csv")

    MMSI = prediction['MMSI'].unique()
    Actual_ship = df[df['MMSI'] == MMSI[0]]

    act_lats = Actual_ship['LAT'].tolist()
    act_lons = Actual_ship['LON'].tolist()
    pred_lats = prediction['LAT'].tolist()
    pred_lons = prediction['LON'].tolist()

    plt.figure()
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
    # plt.show()
    plt.savefig('predPlot.png')
    plt.close()

def actualToPred():
    df = pd.read_csv("boats.csv")
    prediction = pd.read_csv("predictions.csv")

    MMSI = prediction['MMSI'].unique()
    Actual_ship = df[df['MMSI'] == MMSI[0]]

    act_lats = Actual_ship['LAT'].tolist()
    act_lons = Actual_ship['LON'].tolist()
    pred_lats = prediction['LAT'].tolist()
    pred_lons = prediction['LON'].tolist()

    plt.figure()
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.plot(act_lons, act_lats, 'red', marker='.', label='Actual', linestyle='None')
    plt.plot(pred_lons, pred_lats, 'blue', marker='.', label='Predicted', linestyle='None')
    plt.legend(loc='upper right')
    
    for x in range(len(act_lats)-1):
        plt.arrow(act_lons[x], act_lats[x], pred_lons[x]-act_lons[x], pred_lats[x] - act_lats[x], color='green', width=0.00001, head_width=0.00005, length_includes_head=True)
        
    #plt.show()
    plt.savefig('predPlotArrows.png')
    plt.close()
    
#plot()
#actualToPred()

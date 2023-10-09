import matplotlib.pyplot as plt
import pandas as pd

def plot_ship(Actual, prediction):
    
    act_lats = Actual[0]
    act_lons = Actual[1]
    pred_lats = prediction[0]
    pred_lons = prediction[1]
    
    plt.figure()
    plt.title('Actual vs Predicted ship path')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.plot(act_lons, act_lats, 'red', marker='.', label='Actual')
    plt.plot(pred_lons, pred_lats, 'blue', marker='.', label='Predicted')
    plt.legend(loc='upper left')
    
    for x in range(len(lats)-1):
        plt.arrow(lons[x], lats[x], lons[x+1]-lons[x], lats[x+1]-lats[x], color='red', width=0.00001, head_width=0.0003, length_includes_head=True)

    for x in range(len(pred_lats)-1):
        plt.arrow(pred_lons[x], pred_lats[x], pred_lons[x+1]-pred_lons[x], pred_lats[x+1]-pred_lats[x], color='blue', width=0.00001, head_width=0.0003, length_includes_head=True)        
    plt.show()
    plt.savefig('predPlot.png')
 
#Dummy data    
df = pd.read_csv("boats.csv")

actual_ship = df[df['MMSI'] == 367613490]

lats = actual_ship['LAT'].tolist()
lons = actual_ship['LON'].tolist()

actual = lats, lons

pred_lats = actual_ship['LAT'].tolist()
pred_lons = actual_ship['LON'].tolist()

for x in range(len(pred_lats)):
    pred_lats[x] = pred_lats[x] + 0.0001
    pred_lons[x] = pred_lons[x] + 0.0001
prediction = pred_lats, pred_lons

plot_ship(actual, prediction)
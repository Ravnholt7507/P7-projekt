import matplotlib.pyplot as plt
import math

def plot_data(history):
    plt.figure(1)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])

    plt.title('AIS: Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc='upper right')
    plt.show()

def Distance(prediction, target):

    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """

    lat1 = prediction[0]
    lon1 = prediction[1]
    lat2 = target[0]
    lon2 = target[1]

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371.0 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def Average(lst):
    return sum(lst) / len(lst)

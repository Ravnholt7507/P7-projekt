import pandas as pd
import csv
import map
from haversine import haversine, Unit
from math import asin, atan2, cos, degrees, radians, sin

# df = pd.read_csv('AIS_2023_01_01.csv')
df = pd.read_csv('boats.csv')

def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
    '''
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    '''
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(
        sin(a) * sin(d/R) * cos(lat1),
        cos(d/R) - sin(lat1) * sin(lat2)
    )
    return (degrees(lat2), degrees(lon2))

# Take all rows with the same MMSI as the first row with [index]
first = df.loc[df['MMSI'] == df.iloc[1]['MMSI']]
lenght = len(first)

with open('predictions.csv', 'w') as fp:
    fp.truncate()

for i in range(lenght-1):

    parsedPreTime = pd.to_datetime(first.iloc[i]['BaseDateTime'])
    parsedPostTime = pd.to_datetime(first.iloc[i+1]['BaseDateTime'])
    timeDiff = parsedPostTime - parsedPreTime

    timeDiffFloat = timeDiff.total_seconds()

    # Calculating the speed in km/h
    speed = first.iloc[i]['SOG'] * 1.852

    # Calculating the distance travelled in the time difference
    distance = speed * timeDiffFloat / 3600
    distance = round(distance, 2)

    lat = first.iloc[i]['LAT']
    lon = first.iloc[i]['LON']
    bearing = first.iloc[i]['COG']
    lat2, lon2 = get_point_at_distance(lat, lon, distance, bearing)

    # Print MMSI and time
    print('\n')
    print('MMSI: ', first.iloc[i]['MMSI'])
    print('Time: ', first.iloc[i]['BaseDateTime'])

    print('Time difference: ', timeDiff.total_seconds(), ' seconds')
    print('Speed: ', speed, ' km/h')
    print('Distance travelled: ', distance, ' km')
    print('Initial position: ', lat, lon)
    print('Predicted position: ', lat2, lon2)

    # Print distance between initial and predicted position
    # Round to 2 decimals
    next_lat = first.iloc[i+1]['LAT']
    next_lon = first.iloc[i+1]['LON']
    dis = haversine((next_lat, next_lon), (lat2, lon2), unit=Unit.KILOMETERS)
    dis = round(dis, 4)
    print('Distance between actual and predicted position: ', dis, ' km')

    array = []
    array.append(first.iloc[i]['MMSI'])
    array.append(first.iloc[i]['BaseDateTime'])
    array.append(lat2)
    array.append(lon2)
    array.append(first.iloc[i]['SOG'])

    with open('predictions.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if i == 0:
            field = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG']
            writer.writerow(field)
        writer.writerow(array)

map.plot()
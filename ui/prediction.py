import pandas as pd
import csv
import map
from math import asin, atan2, cos, degrees, radians, sin

df = pd.read_csv('boats2.csv')

first = df.groupby('MMSI').apply(lambda t: t.iloc[0])
second = df.groupby('MMSI').apply(lambda t: t.iloc[1])

def get_point_at_distance(lat1, lon1, d, bearing, R=6371):
    """
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    a = radians(bearing)
    lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
    lon2 = lon1 + atan2(
        sin(a) * sin(d/R) * cos(lat1),
        cos(d/R) - sin(lat1) * sin(lat2)
    )
    return (degrees(lat2), degrees(lon2),)


for i in range(len(df['MMSI'].unique())-302):

    print("VESSEL: ", first.iloc[i]['MMSI'])

    # print("CURRENT LOCATION: \n")
    # print("LAT: ", first.iloc[i]['LAT'])
    # print("LON: ", first.iloc[i]['LON'])
    # print("SOG: ", first.iloc[i]['SOG'])
    # print("COG: ", first.iloc[i]['COG'])
    # print("Heading: ", first.iloc[i]['Heading'])
    # print("TIME: ", first.iloc[i]['BaseDateTime'], "\n")

    # print("CALCULATED VECTOR: \n")
    # print("FUTURE LOCATION: \n")
    # print("LAT: ", second.iloc[i]['LAT'])
    # print("LON: ", second.iloc[i]['LON'])
    # print("SOG: ", second.iloc[i]['SOG'])
    # print("COG: ", second.iloc[i]['COG'])
    # print("Heading: ", second.iloc[i]['Heading'])
    # print("TIME: ", second.iloc[i]['BaseDateTime'], "\n")

    # print("VECTOR CALCULATION: \n")

    parsedPreTime = pd.to_datetime(first.iloc[i]['BaseDateTime'])
    parsedPostTime = pd.to_datetime(second.iloc[i]['BaseDateTime'])
    timeDiff = parsedPostTime - parsedPreTime
    print("Time difference: ", timeDiff.total_seconds(), " seconds")

    timeDiffFloat = timeDiff.total_seconds()

    # Calculating the speed in km/h
    speed = first.iloc[i]['SOG'] * 1.852
    print("Speed: ", speed, " km/h")

    # Calculating the distance travelled in the time difference
    distance = speed * timeDiffFloat / 3600
    print("Distance travelled: ", distance, " km")

    lat = first.iloc[i]['LAT']
    lon = first.iloc[i]['LON']
    bearing = first.iloc[i]['COG']
    lat2, lon2 = get_point_at_distance(lat, lon, distance, bearing)

    print(lat2, lon2)

    array = []
    array.append(first.iloc[i]['MMSI'])
    array.append(lat2)
    array.append(lon2)

with open('predictions.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["MMSI", "LAT", "LON"]
    writer.writerow(field)
    writer.writerow(array)

map.plot()

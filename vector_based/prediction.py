import pandas as pd
import csv
from haversine import haversine, Unit
from math import asin, atan2, cos, degrees, radians, sin
import statistics

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
    lon2 = lon1 + atan2(sin(a) * sin(d/R) * cos(lat1), cos(d/R) - sin(lat1) * sin(lat2))
    return (degrees(lat2), degrees(lon2))

def predict(MMSI, df, file_path):
    ship = df[df['MMSI'] == int(MMSI)]
    length = len(ship)
    empty = False

    with open(file_path, 'r') as file:
        csv_dict = [row for row in csv.DictReader(file)]
        if len(csv_dict) == 0:
            empty = True

    with open('data/predictions.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if empty:
            field = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG']
            writer.writerow(field)

        for i in range(length - 1):
            parsedPreTime = pd.to_datetime(ship.iloc[i]['BaseDateTime'])
            parsedPostTime = pd.to_datetime(ship.iloc[i + 1]['BaseDateTime'])
            timeDiff = (parsedPostTime - parsedPreTime).total_seconds()

            # Calculating the speed in km/h
            speed = ship.iloc[i]['SOG'] * 1.852

            # Calculating the distance travelled in the time difference
            distance = speed * timeDiff / 3600
            distance = round(distance, 2)

            lat = ship.iloc[i]['LAT']
            lon = ship.iloc[i]['LON']
            bearing = ship.iloc[i]['COG']
            lat2, lon2 = get_point_at_distance(lat, lon, distance, bearing)

            next_lat = ship.iloc[i + 1]['LAT']
            next_lon = ship.iloc[i + 1]['LON']
            dis = haversine((next_lat, next_lon), (lat2, lon2), unit=Unit.KILOMETERS)
            dis = round(dis, 4)

            array = [ship.iloc[i]['MMSI'], ship.iloc[i]['BaseDateTime'], lat2, lon2, ship.iloc[i]['SOG']]
            writer.writerow(array)

def predict2(MMSI, df, file_path):
    ship = df[df['MMSI'] == int(MMSI)]
    length = len(ship)
    empty = False

    with open(file_path, 'r') as file:
        csv_dict = [row for row in csv.DictReader(file)]
        if len(csv_dict) == 0:
            empty = True

    with open('data/predictions.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if empty:
            field = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'SOG']
            writer.writerow(field)

        for i in range(length - 1):
            time = 180  # 1 minute

            # Calculating the speed in km/h
            speed = ship.iloc[i]['SOG'] * 1.852

            # Calculating the distance travelled in the time difference
            distance = speed * time / 3600
            distance = round(distance, 2)

            lat = ship.iloc[i]['LAT']
            lon = ship.iloc[i]['LON']
            bearing = ship.iloc[i]['COG']
            lat2, lon2 = get_point_at_distance(lat, lon, distance, bearing)

            next_lat = ship.iloc[i + 1]['LAT']
            next_lon = ship.iloc[i + 1]['LON']
            dis = haversine((next_lat, next_lon), (lat2, lon2), unit=Unit.KILOMETERS)
            dis = round(dis, 4)

            array = [ship.iloc[i]['MMSI'], ship.iloc[i]['BaseDateTime'], lat2, lon2, ship.iloc[i]['SOG']]
            writer.writerow(array)

def all_ships(df):
    MMSI = df['MMSI'].unique()
    ships = len(MMSI)
    for i in range(ships):
        predict2(MMSI[i],df,'data/predictions.csv')

def check_range(distance, range_index):
    start, end = dist_intv[range_index]
    return start <= distance <= end

def find_dis_index(dist_intv, distance):
    for i, (start, end) in enumerate(dist_intv):
        if start <= distance < end:
            return i

def predict_intv(df):
    grouped = df.groupby('MMSI')
    grouped_list = list(df)
    num_dist_intv = 1
    dist_intv = [(0, 3), (3, 5), (5, 1000000000)]
    available_point = True
    stat_array = [[] for _ in range(len(dist_intv))]
    total_predictions = 0

    # Assumes at least 2 datapoints per group.
    for name, group in grouped:
        for current_point in range(group.shape[0]-1):
            i = 0
            for comparison_point in range(current_point+1, group.shape[0]-1):
                i = i+1
                # print("CURRENT POINT: ", current_point)
                # print("COMPARISON POINT: ", comparison_point)
                dis = haversine((group.iloc[comparison_point]['LAT'], group.iloc[comparison_point]['LON']), (
                    group.iloc[current_point]['LAT'], group.iloc[current_point]['LON']), unit=Unit.KILOMETERS)
                dis = round(dis, 4)

                parsedPreTime = pd.to_datetime(
                    group.iloc[current_point]['BaseDateTime'])
                parsedPostTime = pd.to_datetime(
                    group.iloc[comparison_point]['BaseDateTime'])

                timeDiff = parsedPostTime - parsedPreTime
                timeDiffFloat = timeDiff.total_seconds()

                speed = group.iloc[current_point]['SOG'] * 1.852

                distance = speed * timeDiffFloat / 3600
                distance = round(distance, 2)

                prediction = get_point_at_distance(
                    group.iloc[current_point]['LAT'], group.iloc[current_point]['LON'], distance, group.iloc[current_point]['COG'])
                error = haversine((group.iloc[comparison_point]['LAT'], group.iloc[comparison_point]['LON']), (
                    prediction[0], prediction[1]), unit=Unit.KILOMETERS)
                error = round(error, 4)

                stat_array[find_dis_index(dist_intv, dis)].append(error)
                total_predictions = total_predictions+1

    print("\nTotal predictions: ", total_predictions)
    i = 0
    for row in stat_array:
        print("\nFor distance interval:", dist_intv[i])
        print("Number of predictions: ", len(row))
        print("Avg. error: ", round(sum(row)/len(row),2))
        print("Mean error: ", round(statistics.median(row),2))
        i = i + 1
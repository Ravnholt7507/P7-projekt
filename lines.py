from geopy.distance import geodesic

def scale_the_cock(coord1, coord2, speed, desired_time):
    # Calculate the original distance in meters
    original_distance = geodesic(coord1, coord2).meters

    # Calculate the distance travelled in the desired time
    distance_travelled = speed * desired_time

    # Calculate the scaling factor
    scaling_factor = distance_travelled / original_distance

    # Interpolate the new coordinates
    scaled_coords = [
        coord1[0] + (coord2[0] - coord1[0]) * scaling_factor,
        coord1[1] + (coord2[1] - coord1[1]) * scaling_factor
    ]

    return tuple(scaled_coords)

# Example usage
coord1 = (37.7749, -122.4194)
coord2 = (34.0522, -118.2437)
speed = 100
desired_time = 5000  # 5000 seconds

scaled_coordinates = scale_the_cock(coord1, coord2, speed, desired_time)

print("Original Coordinates:", coord2)
print("Scaled Coordinates:", scaled_coordinates)
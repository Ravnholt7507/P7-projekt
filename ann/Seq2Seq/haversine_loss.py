import torch

def denormalize(coords, lat_min, lat_max, lon_min, lon_max):

  lat_min, lat_max = map(torch.tensor, (lat_min, lat_max))
  lon_min, lon_max = map(torch.tensor, (lon_min, lon_max))

  coords = torch.tensor(coords, dtype=torch.float32) if not isinstance(coords, torch.Tensor) else coords

  lat = coords[..., 1] * (lat_max - lat_min) + lat_min
  lon = coords[..., 2] * (lon_max - lon_min) + lon_min

  return torch.stack((lat, lon), -1)

def haversine_distance(preds, target):
  lat1, lon1 = preds[..., 0], preds[..., 1]
  lat2, lon2 = target[..., 0], target[..., 1]
  radius = 6371  # Earth radius in kilometers'

  # Convert latitude and longitude from degrees to radians
  lat1, lon1, lat2, lon2 = map(torch.deg2rad, [lat1, lon1, lat2, lon2])

  # Compute differences
  dlat = lat2 - lat1
  dlon = lon2 - lon1

  # Apply the Haversine formula
  a = torch.sin(dlat / 2)**2 + torch.cos(lat1) * torch.cos(lat2) * torch.sin(dlon / 2)**2

  epsilon = 0.00000000001
  a += epsilon
  c = 2 * torch.asin(torch.sqrt(a))
  distance = radius * c

  return distance

def haversine(y_pred, y_true, lat_min, lat_max, lon_min, lon_max):
  lat_min = lat_min
  lat_max = lat_max
  lon_min = lon_min
  lon_max = lon_max

  preds_denorm = denormalize(y_pred, lat_min, lat_max, lon_min, lon_max)
  target_denorm = denormalize(y_true, lat_min, lat_max, lon_min, lon_max)

  #print("preds_denormalized: ", preds_denorm)
  #print("targets_denormalized: ", target_denorm)

  loss = haversine_distance(preds_denorm, target_denorm)

  return loss.mean()
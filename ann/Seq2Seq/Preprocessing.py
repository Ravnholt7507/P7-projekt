from sklearn.preprocessing import MinMaxScaler

def normalize(df):
    # We'll use MinMaxScaler for normalization, which will scale each feature to the range [0, 1]
    scaler = MinMaxScaler()

    # We won't scale the 'MMSI' or 'Timestamp' columns
    features_to_scale = ['LAT', 'LON', 'SOG', 'COG']
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale])

def denormalize(scaler, df):
    predictions_flat = df.reshape(-1, 4)  # Shape: (batch_size * timesteps, 2)

    # Apply inverse_transform
    predictions_denorm = scaler.inverse_transform(predictions_flat)

    # Reshape back to original shape if necessary
    predictions_original_shape = predictions_denorm.reshape(df.shape)
    return predictions_original_shape

def GetMinMax(df):
    lat_max = df['LAT'].max()
    lat_min = df['LAT'].min()
    lon_max = df['LON'].max()
    lon_min = df['LON'].min()
    return lat_max, lat_min, lon_max, lon_min
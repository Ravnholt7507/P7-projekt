from sklearn.preprocessing import MinMaxScaler

def normalize(df):
    scaler = MinMaxScaler()
    features_to_scale = ['LAT', 'LON', 'SOG', 'COG']
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale])
    return df, scaler

def denormalize(scaler, tensor):
    predictions_flat = tensor.reshape(-1, 4)  # Shape: (batch_size * timesteps, 2)

    predictions_denorm = scaler.inverse_transform(predictions_flat)

    predictions_original_shape = predictions_denorm.reshape(tensor.shape)
    return predictions_original_shape

def GetMinMaxCoords(df):
    print(df.info())
    lat_max = df['LAT'].max()
    lat_min = df['LAT'].min()
    lon_max = df['LON'].max()
    lon_min = df['LON'].min()
    return lat_max, lat_min, lon_max, lon_min
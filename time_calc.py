import pandas as pd
import numpy as np

df = pd.read_csv('data/AIS_2023_01_01.csv')

# print average time between each position per MMSI
df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
df = df.sort_values(by=['MMSI', 'BaseDateTime'])
df['time_diff'] = df.groupby('MMSI')['BaseDateTime'].diff()


# Print MMSI and time difference for the largest time difference
print(df.loc[df['time_diff'].idxmax()])

# Print the 10 largest time differences
print(df.nlargest(10, 'time_diff'))
# Save them in a CSV file
df.nlargest(10, 'time_diff').to_csv('data/largest_time_diff.csv', index=False)

# Print MMSI and time difference for the smallest time difference
print(df.loc[df['time_diff'].idxmin()])

# Print average time difference for all MMSI
print(df['time_diff'].mean())

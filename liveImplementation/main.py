import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import models.AIPredModels as AIModels
import simulation as simulationClass
import globalVariables as globals
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

start_time = time.time()

def interpolater(df):
    df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
    df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)

    frequency = '2T' 

    grouped = df.groupby('MMSI')
    interpolated_data = []

    for mmsi, group in tqdm(grouped, desc="Processing vessels"):
        group.set_index('BaseDateTime', inplace=True)
        resampled = group.resample(frequency).first()
        resampled = resampled.infer_objects(copy=False)
        interpolated = resampled.interpolate(method='linear')
        interpolated['MMSI'] = mmsi
        interpolated_data.append(interpolated)
    interpolated_df = pd.concat(interpolated_data)
    interpolated_df.reset_index(inplace=True)
    return interpolated_df

limit = 50000
df = pd.read_csv("../data/AIS_2023_01_01.csv")
# df = df.drop(columns=['Heading', 'VesselName', 'IMO', 'CallSign','VesselType', 'Status', 'Length', 'Width', 'Draft', 'Cargo', 'TransceiverClass'])
df = df.sort_values(by=['MMSI', 'BaseDateTime'], ascending=True)

#Initialize working data and output data
interpolated_data = interpolater(df)
output_CSV = interpolated_data.copy()
output_CSV['predictedLAT'] = None
output_CSV['predictedLON'] = None
output_CSV['locationThresholdLAT'] = None
output_CSV['locationThresholdLON'] = None
output_CSV['radiusThreshold'] = None
output_CSV['thresholdExceeded'] = None
output_CSV['currentModel'] = None

interpolated_data = interpolated_data.groupby('MMSI')

simulationOutput = np.empty((0, 7))
print("Running simulation...")
#Run simulation for each unique boat
for name, group in interpolated_data:
    shore_instance = shore.shoreEntity(group.iloc[0])
    boat_instance = boat.boatEntity(group.iloc[0])
    simulation_instance = simulationClass.simulation(group, shore_instance, boat_instance)
    simulationOutput =np.vstack((simulationOutput, simulation_instance.run_simulation())) 

#Append output metrics to copy of working CSV file -> gives complete outputCSV
for col_idx, col_name in enumerate(output_CSV.columns[6:]):
    output_CSV[col_name] = [row[col_idx] for row in simulationOutput]

#Save dataframe as CSV
output_CSV.to_csv('../data/output.csv')

print("Simulation complete!")
print("in %s seconds" % (round(time.time() - start_time, 2)))
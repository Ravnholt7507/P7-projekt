from sklearn.preprocessing import MinMaxScaler
import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import interDataHandler as dataHandler
import simulation as simulationClass
import globalVariables as gv
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

start_time = time.time()

#Initialize working data and output data

interpolated_data = dataHandler.interpolater()
interpolated_data.to_csv('../data/interpolated_data.csv', index=False)

interpolated_data = pd.read_csv('../data/interpolated_data.csv')
scaler = dataHandler.Fit_Scaler_To_Data(interpolated_data)
# gv.scaler = scaler

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
i = 1

length = len(interpolated_data)
# Run simulation for each unique boat
for name, group in tqdm(interpolated_data, desc="Running simulation"):
    shore_instance = shore.shoreEntity(group.iloc[0])
    boat_instance = boat.boatEntity(group.iloc[0])
    simulation_instance = simulationClass.simulation(group, shore_instance, boat_instance)
    simulationOutput = np.vstack((simulationOutput, simulation_instance.run_simulation()))
    
    i = i+1

# Append output metrics to copy of working CSV file -> gives complete outputCSV
for col_idx, col_name in enumerate(output_CSV.columns[6:]):
    output_CSV[col_name] = [row[col_idx] for row in simulationOutput]

# Save dataframe as CSV
output_CSV.to_csv('../data/output.csv')

# Count all rows where the threshold was exceeded
thresholdExceeded = output_CSV.loc[output_CSV['thresholdExceeded'] == True]
print("Threshold exceeded in %s cases" % (len(thresholdExceeded)))


print("Simulation complete!")
print("in %s seconds" % (round(time.time() - start_time, 2)))
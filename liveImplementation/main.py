import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import models.AIPredModels as AIModels
import interDataHandler as dataHandler
import simulation as simulationClass
import globalVariables as globals
import pandas as pd
import numpy as np
import time

start_time = time.time()

#Initialize working data and output data
interpolated_data = dataHandler.interpolater()
interpolated_data.to_csv('../data/interpolated_data.csv', index=False)

#DO NOT DELETE - COMMENT OUT IF NEEDED
#interpolated_data = pd.read_csv('../data/interpolated_data.csv')

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
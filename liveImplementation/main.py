import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import models.AIPredModels as AIModels
import data.interDataHandler as dataImporter
import simulation as simulationClass
import globalVariables as globals
import pandas as pd
import os
import numpy as np

timeIntervals = globals.timeIntervals

interpolated_data = pd.read_csv(os.path.join(os.getcwd(), 'liveImplementation' , 'data', 'interpolated_data.csv'))
globals.output_CSV = interpolated_data.copy()
globals.output_CSV['predictedLAT'] = None
globals.output_CSV['predictedLON'] = None
globals.output_CSV['locationThreshold'] = None
globals.output_CSV['radiusThreshold'] = None
globals.output_CSV['thresholdExceeded'] = None
globals.output_CSV['currentModel'] = None

interpolated_data = interpolated_data.groupby('MMSI')

simulationOutput = np.empty((0, 6))

for name, group in interpolated_data:
    shore_instance = shore.shoreEntity(group.iloc[0])
    boat_instance = boat.boatEntity(group.iloc[0])
    simulation_instance = simulationClass.simulation(group, shore_instance, boat_instance)
    simulationOutput =np.vstack((simulationOutput, simulation_instance.run_simulation())) 

print(simulationOutput.shape[0])


for col_idx, col_name in enumerate(globals.output_CSV.columns[6:]):
    globals.output_CSV[col_name] = [row[col_idx] for row in simulationOutput]

globals.output_CSV.to_csv(os.path.join(os.getcwd(), 'liveImplementation' , 'data', 'output.csv'))
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

#Intialize timeIntervals
timeIntervals = globals.timeIntervals

interpolated_data = dataImporter.cleanseData(timeIntervals)

#Initialize working data and output data
interpolated_data = pd.read_csv(os.path.join(os.getcwd(), 'liveImplementation' , 'data', 'interpolated_data.csv'))
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
output_CSV.to_csv(os.path.join(os.getcwd(), 'liveImplementation' , 'data', 'output.csv'))
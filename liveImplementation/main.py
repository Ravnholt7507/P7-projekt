import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import models.AIPredModels as AIModels
import data.interDataHandler as dataImporter
import simulation as simulationClass
import globalVariables as globals
import pandas as pd
import os

timeIntervals = globals.timeIntervals

test = pd.read_csv(os.path.join(os.getcwd(), 'liveImplementation' , 'data', 'interpolated_data.csv'))

test = test.groupby('MMSI')


for name, group in test:
    shore_instance = shore.shoreEntity(group.iloc[0])
    boat_instance = boat.boatEntity(group.iloc[0])
    simulation_instance = simulationClass.simulation(group, shore_instance, boat_instance)
    simulation_instance.run_simulation()
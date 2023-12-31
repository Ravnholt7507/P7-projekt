from sklearn.preprocessing import MinMaxScaler
import liveImplementation.actors.shore as shore
import liveImplementation.actors.boat as boat
import liveImplementation.models.traditionPredModels as tradModels
import liveImplementation.DataHandler as dh
import liveImplementation.simulation as simulationClass
import liveImplementation.settings as s
import liveImplementation.filter as filter
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

def liveImplementation():
    start_time = time.time()

    #Initialize working data and output data
    # data = (1,2,3,4,5,6,7,8,9,10)
    # ais_input = np.array(data)
    ais_input = filter.filter()
    # Use this data:
    # datapath = '../data/AIS_2023_01_01.csv'
    datapath = 'data/filtered_limited.csv'
    # datapath = '../data/filtered_unlimited.csv'

    print("Reading data from: ", datapath)

    interpolated_data, mapping_dict = dh.interpolater(datapath)
    interpolated_data.to_csv('data/interpolated_data.csv', index=False)

    interpolated_data = pd.read_csv('data/interpolated_data.csv')

    #These three lines are only for fitting data to our normalizer for AIBased prediction
    all_data_for_fitting = pd.read_csv('data/interpolated_complete.csv')
    scaler = dh.Fit_Scaler_To_Data(all_data_for_fitting)
    s.scaler = scaler

    interpolated_data = interpolated_data[0:20]

    print("Hvor mange AIS punkter: ", len(interpolated_data))

    output_DF = interpolated_data.copy()
    output_DF['predictedLAT'] = None
    output_DF['predictedLON'] = None
    output_DF['radiusThreshold'] = None
    output_DF['thresholdExceeded'] = None
    output_DF['currentModel'] = None

    g_interpolated_data = interpolated_data.groupby('MMSI')

    simulationOutput = np.empty((0, 5))

    length = len(g_interpolated_data)
    # Run simulation for each unique boat
    for name, group in tqdm(g_interpolated_data, desc="Running simulation"):
        # print("\n \n Group by mmsi: ", name)
        shore_instance = shore.shoreEntity(group.iloc[0])
        boat_instance = boat.boatEntity(group.iloc[0])
        simulation_instance = simulationClass.simulation(group, shore_instance, boat_instance)
        simulationOutput = np.vstack((simulationOutput, simulation_instance.run_simulation()))

    # Append output metrics to copy of working CSV file -> gives complete output_DF
    for col_idx, col_name in enumerate(output_DF.columns[7:]):
        output_DF[col_name] = [row[col_idx] for row in simulationOutput]

    # Save dataframe as CSV
    #output_DF['VesselName'] = interpolated_data['MMSI'].map(mapping_dict)
    
    output_DF = dh.add_time(output_DF)
    
    output_DF.to_csv('data/output.csv', index=False)
    output_df = pd.read_csv('data/output.csv')

    #PRINT PERFORMANCE METRICS
    print("\nSimulation complete!")
    print("in %s seconds\n" % (round(time.time() - start_time, 2)))

    thresholdExceeded_Count = dh.countInstances('thresholdExceeded', True, output_df)
    VectorModel_Count = dh.countInstances('currentModel', 'vectorBasedModel', output_df)
    PointModel_Count = dh.countInstances('currentModel', 'pointBasedModel', output_df)
    COGModel_Count = dh.countInstances('currentModel', 'COGBasedModel', output_df)
    AIModel_Count = dh.countInstances('currentModel', 'AImodel', output_df)
    HeadingModel_Count = dh.countInstances('currentModel', 'HeadingBasedModel', output_df)

    print("AIModelCount: ", len(AIModel_Count))
    print("simulationOutput: ", len(simulationOutput))

    print("Total AIS updates: %s" % (len(thresholdExceeded_Count)))
    print("Reduced AIS updates by:",round((len(ais_input)-len(thresholdExceeded_Count))/len(ais_input)*100,1), "%\n")

    print("VectorBasedModel in use",dh.calcPartPerc(VectorModel_Count, simulationOutput), "%")
    print("PointBasedModel in use",dh.calcPartPerc(PointModel_Count, simulationOutput), "%")
    print("COGModel in use",dh.calcPartPerc(COGModel_Count, simulationOutput), "%")
    print("AIModel in use",dh.calcPartPerc(AIModel_Count, simulationOutput), "%")
    print("HeadingModel in use",dh.calcPartPerc(HeadingModel_Count, simulationOutput), "%")
import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import models.AIPredModels as AIModels
import interDataHandler as dataHandler
import simulation as simulationClass
import globalVariables as gv
import pandas as pd
import numpy as np
import time
from tqdm import tqdm
import time


# gv.tts = gv.TextToSpeech(voice_id=1, speed=170)
# gv.tts.toggle_speech(enable=False)
# gv.tts.speak("\nNarration is enabled to enhance program understanding. To run program normally, please pass False as boolean value to the toggle speech function found in main.\n\n")
# gv.tts.speak("Initiating program.\n\n")

start_time = time.time()

#Initialize working data and output data

# gv.tts.speak("Interpolating data. Please wait.")
# interpolated_data = dataHandler.interpolater()
# interpolated_data.to_csv('../data/interpolated_data.csv', index=False)
# gv.tts.speak("Interpolation process completed.\n\n")

interpolated_data = pd.read_csv('../data/interpolated_data.csv')

output_CSV = interpolated_data.copy()
output_CSV['predictedLAT'] = None
output_CSV['predictedLON'] = None

output_CSV['locationThresholdLAT'] = None
output_CSV['locationThresholdLON'] = None
output_CSV['radiusThreshold'] = None
output_CSV['thresholdExceeded'] = None
output_CSV['currentModel'] = None

interpolated_data = interpolated_data.groupby('MMSI')

# gv.tts.speak("Executing simulation.")
simulationOutput = np.empty((0, 7))
i = 1

length = len(interpolated_data)
# Run simulation for each unique boat
for name, group in tqdm(interpolated_data, desc="Running simulation"):
    # gv.tts.speak("Creating instance of shore object.\n\n")
    shore_instance = shore.shoreEntity(group.iloc[0])
    # gv.tts.speak("Creating instance of boat object.\n\n")
    boat_instance = boat.boatEntity(group.iloc[0])
    # gv.tts.speak("   Simulating group {} of {} total groups\n", i, length)
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
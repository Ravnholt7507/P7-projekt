import models.traditionPredModels as traditionalModels
import random
import math
import numpy as np
import globalVariables as gv

def modelPicker(lastKnownLocations):
    '''
    sMake a new model picker that uses the last known location to determine which model to use
    The models are:
        - Point based
        - COG based
        - Vector based
        - AI based
        - If Heading = 511, go to next cases
    '''
    rateOfTurn = calcRateOfTurn(lastKnownLocations)

    if (lastKnownLocations[-1]['SOG']<0.3):
        return traditionalModels.pointBasedModel(lastKnownLocations[-1])
    
    if (rateOfTurn >= 2 and len(lastKnownLocations) == 10):
          
          return traditionalModels.AIBasedModel(lastKnownLocations)

    if (not(lastKnownLocations[-1]['COG'] != 360)):
          gv.counter = gv.counter+1

    if (lastKnownLocations[-1]['COG'] != 360):
        return traditionalModels.COGBasedModel(lastKnownLocations[-1])
    
    if (lastKnownLocations[-1]['Heading'] != 511): 
        return traditionalModels.HeadingBasedModel(lastKnownLocations[-1])
    
    if (lastKnownLocations[-1]['COG'] != 360 and lastKnownLocations[-1]['Heading'] != 511 and len(lastKnownLocations)>1):
          return traditionalModels.vectorBasedModel(lastKnownLocations)
    
    else:
        return traditionalModels.pointBasedModel(lastKnownLocations[-1])
    

def calcRateOfTurn(queue):
    if len(queue)>1:
        
        if queue[-1]['COG'] != 360 and queue[-2]['COG'] != 360:
            locations = np.array([(entry['COG']) for entry in queue])   
            last_two_cog_locations = locations[-2:]
            cog_diff = np.diff(last_two_cog_locations)
            return abs(cog_diff)
        elif queue[-1]['Heading'] != 511 and queue[-2]['Heading'] != 511:
            locations = np.array([(entry['Heading']) for entry in queue])   
            last_two_Heading_locations = locations[-2:]  
            heading_diff = np.diff(last_two_Heading_locations)
            return abs(heading_diff)
    elif len(queue) > 2:
        # Convert deque to a NumPy array and extract 'LAT' and 'LON'
        locations = np.array([(entry['LAT'], entry['LON']) for entry in queue])

        # Take the last three locations
        last_three_locations = locations[-3:] 
        vectors = np.diff(last_three_locations, axis=0)

        #Compute angles
        angles = np.arctan2(vectors[:, 1], vectors[:, 0])
        angle_diff = np.diff(angles)[-1]
        angle_diff_degrees = np.degrees(angle_diff)

        return abs(angle_diff_degrees)
    else:
          return 0
    
    
      

def average_COG(dataframe):
	total = 0
	missing_COGs = 0
    
	for x in range(len(dataframe)):
		if dataframe[x]['COG'] != None:
			for y in range(x+1 ,len(dataframe)):
				if dataframe[y]['COG'] != None:
					total += abs(dataframe[x]['COG']) - dataframe[y]['COG']
					break
		else:
			missing_COGs =+ 1

	return (total / (len(dataframe) - missing_COGs))

import models.traditionPredModels as traditionalModels

def modelPicker(lastKnownLocations):
        '''
        Make a new model picker that uses the last known location to determine which model to use
        The models are:
            - Point based
            - COG based
            - Vector based
            - AI based
            - If Heading = 511, go to next case
        '''
        '''
        if lastKnownLocations[-1]['SOG'] * 1.852 < 0.1 or (lastKnownLocations[-1]['COG'] == None and len(lastKnownLocations) < 2 and lastKnownLocations[-1]['SOG'] * 1.852 < 0.1):
            if lastKnownLocations[-1]['SOG']>200:
                print(lastKnownLocations[-1]['SOG'])
            return traditionalModels.pointBasedModel(lastKnownLocations[-1])        
        else:
            if lastKnownLocations[-1]['SOG']>200:
                print(lastKnownLocations[-1]['SOG'])            
            return traditionalModels.COGBasedModel(lastKnownLocations[-1])
        elif len(lastKnownLocations) >= 2 and lastKnownLocations[-1]['SOG'] * 1.852 > 0.3:
            return traditionalModels.vectorBasedModel(lastKnownLocations)
        
        elif len(lastKnownLocations) < 2 and lastKnownLocations[-1]['COG'] == None and lastKnownLocations[-1]['SOG'] * 1.852 > 0.3:
             return traditionalModels.HeadingBasedModel(lastKnownLocations)
        
        elif len(lastKnownLocations) >= 8 and average_COG(lastKnownLocations) > 5:
            return traditionalModels.AIBasedModel(lastKnownLocations)
        
        else:
            #print("Default Case")
            return traditionalModels.pointBasedModel(lastKnownLocations[-1]) 

        '''
		
        if len(lastKnownLocations) == 10 and lastKnownLocations[-1]['SOG'] * 1.852 > 3:
            return traditionalModels.AIBasedModel(lastKnownLocations)  
        else:
            return traditionalModels.pointBasedModel(lastKnownLocations[-1])


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

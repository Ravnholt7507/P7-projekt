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
   
        if lastKnownLocations[-1]['SOG'] * 1.852 < 0.1:
            return traditionalModels.pointBasedModel(lastKnownLocations[-1])
        else:
            return traditionalModels.COGBasedModel(lastKnownLocations[-1]) 



def average_COG(Dataframe):
	total = 0
	Missing_COCKS = 0
    
	for x in range(len(Dataframe)):
		if Dataframe[x]['COG'] != None:
			for y in range(x+1 ,len(Dataframe)):
				if Dataframe[y]['COG'] != None:
					total += abs(Dataframe[x]['COG']) - Dataframe[y]['COG']
					break
		else:
			Missing_COCKS =+ 1

	return (total / (len(Dataframe) - Missing_COCKS))
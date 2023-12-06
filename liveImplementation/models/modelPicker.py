import models.traditionPredModels as traditionalModels

def modelPicker(lastKnownLocations):
        '''
        Make a new model picker that uses the last known location to determine which model to use
        The models are:
                - Point based
                - COG based
                - Vector based
                - AI based
        '''
        if lastKnownLocations[-1]['SOG'] * 1.852 < 0.1:
                return traditionalModels.pointBasedModel(lastKnownLocations[-1])
        elif lastKnownLocations[-1]['SOG'] * 1.852 > 0.3:
                return traditionalModels.COGBasedModel(lastKnownLocations[-1])
        elif len(lastKnownLocations) == 3:
                return traditionalModels.vectorBasedModel(lastKnownLocations)
        #else:
        #        return traditionalModels.AIPredictionModel(lastKnownLocations)
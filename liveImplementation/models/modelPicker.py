import models.traditionPredModels as traditionalModels
import models.AIPredModels as AIModels

def modelPicker(lastKnownLocations):
        if lastKnownLocations[-1]['SOG'] * 1.852 < 0.3:
                return traditionalModels.pointBasedModel(lastKnownLocations[-1])
        else:
                return traditionalModels.COGBasedModel(lastKnownLocations[-1])
        #If "not first run" + other conditions
                #return vector based

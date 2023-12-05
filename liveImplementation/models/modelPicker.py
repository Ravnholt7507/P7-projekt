import models.traditionPredModels as traditionalModels
import models.AIPredModels as AIModels
import globalVariables as gv

def modelPicker(lastKnownLocations):
        """ if lastKnownLocations[-1]['SOG'] * 1.852 < 0.3:
                return traditionalModels.pointBasedModel(lastKnownLocations[-1])
        elif lastKnownLocations[-1]['SOG'] * 1.852 > 0.3:
                return traditionalModels.COGBasedModel(lastKnownLocations[-1])
        else:
                return traditionalModels.vectorBasedModel(lastKnownLocations) """
        if len(lastKnownLocations)>99999999:
                gv.tts.speak("     Model picker returning Vector Based Model.")
                return traditionalModels.vectorBasedModel(lastKnownLocations)
        else:
                gv.tts.speak("     Model picker returning Course Over Ground model.")
                return traditionalModels.COGBasedModel(lastKnownLocations[-1])
        #If "not first run" + other conditions
                #return vector based

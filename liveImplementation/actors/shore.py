import models.modelPicker as mp
from collections import deque
import globalVariables as gv


class shoreEntity:
    def __init__(self, currentLocation) -> None:
        self.last_known_locations = deque(maxlen=10)
        self.last_known_locations.append(dict(currentLocation))   
        gv.tts.speak("     Shore initializing model.")     
        self.current_model = mp.modelPicker(self.last_known_locations)
        gv.tts.speak("     Shore initializing threshold.")
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        gv.tts.speak("     Shore intializing predicted location as current location.\n")
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        self.updateRecieved = False

    #Updates current knowledge -> is called from boat when locationThreshold has been exceeded
    def recieveLocationUpdate(self, lastKnownLocations):
        gv.tts.speak("     Shore recieving update from boat.")
        gv.tts.speak("     Shore updating location intel and prediction model.")
        self.last_known_locations = lastKnownLocations
        gv.tts.speak("     Shore choosing new model.")
        self.current_model = mp.modelPicker(self.last_known_locations)
        gv.tts.speak("     Shore updating internal threshold and predicted location.")
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (self.last_known_locations[-1]['LAT'], self.last_known_locations[-1]['LON'])
        self.updateRecieved = True

    #Simulates normal shore behaviour
    def shoreBehaviour(self):
        #Are we sure it shouldn't run predictionAlgorithm when updateRecieved == True?
        if self.updateRecieved == False:
            gv.tts.speak("     Shore running prediction algorithm and updating internal predicted location.")
            self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
            gv.tts.speak("     Shore giving control back to simulation\n\n")
        else:
            gv.tts.speak("     Shore not running predictin method.")
            self.updateRecieved = False
            gv.tts.speak("     Shore giving control back to simulation\n\n")
import liveImplementation.models.modelPicker as mp
from collections import deque
import liveImplementation.settings as s

class shoreEntity:
    def __init__(self, currentLocation) -> None:
        self.last_known_locations = deque(maxlen=10)
        self.last_known_locations.append(dict(currentLocation))    
        self.current_model = mp.modelPicker(self.last_known_locations)
        self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        self.updateRecieved = False

    #Updates current knowledge -> is called from boat when locationThreshold has been exceeded
    def recieveLocationUpdate(self, lastKnownLocations):
        self.last_known_locations = lastKnownLocations
        self.current_model = mp.modelPicker(self.last_known_locations)
        self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (self.last_known_locations[-1]['LAT'], self.last_known_locations[-1]['LON'])
        self.updateRecieved = True

    #Simulates normal shore behaviour
    def shoreBehaviour(self):
        if self.updateRecieved == False:
            self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
        else:
            self.updateRecieved = False

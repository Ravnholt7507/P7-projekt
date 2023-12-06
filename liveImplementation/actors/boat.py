import models.modelPicker as mp
from haversine import haversine
from collections import deque
import numpy as np

class boatEntity:
    def __init__(self, currentLocation) -> None:
        # gv.tts.speak("     Initializing boat object.")
        self.last_known_locations = deque(maxlen=10)
        self.last_known_locations.append(dict(currentLocation))

        self.current_index = 0
        # gv.tts.speak("     Boat initializing current model.")
        self.current_model = mp.modelPicker(self.last_known_locations)
        # gv.tts.speak("     Boat initializing threshold")
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        # gv.tts.speak("     Boat initializing predicted location as current location.\n")
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        self.thresholdExceeded = False

    def exceedsThreshold(self) -> bool:
        # gv.tts.speak("     Boat checking threshold breaches.")
        thresholdPoint = (self.locationThreshold[0], self.locationThreshold[1])
        actualLocationPoint = (self.currentLocation['LAT'], self.currentLocation['LON'])
        predictedPoint = (self.predictedLocation[0], self.predictedLocation[1])
        realDistance = haversine(thresholdPoint, actualLocationPoint)
        predictedDistance = haversine(thresholdPoint, predictedPoint)
        return realDistance > self.radiusThreshold or predictedDistance > self.radiusThreshold

    #Sends update to shore when locationThreshold has been exceeded
    def updateShore(self, shoreEntity) -> None:
        # gv.tts.speak("     Boat sending location update to shore.")
        shoreEntity.recieveLocationUpdate(self.last_known_locations)

    #Updates internal models of boat when locationThreshold has been exceeded
    def updateBoat(self, currentLocation):
        # gv.tts.speak("     Boat updating internal boat location and prediction model.")
        #("BOAT: UpdateBoat")
        self.last_known_locations.append(dict(currentLocation))
        # gv.tts.speak("     Boat choosing new model.")
        self.current_model = mp.modelPicker(self.last_known_locations)
        # gv.tts.speak("     Boat determining new threshold and predicted location.")
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (self.currentLocation['LAT'], self.currentLocation['LON'])

    #Simulates normal boat behaviour
    def boatBehaviour(self, currentLocation, shoreEntity):
        # gv.tts.speak("     Boat sailing. Location updated.")
        self.currentLocation = currentLocation
        # gv.tts.speak("     Boat running prediction algorithm. Internal predicted location updated.")
        self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
     
        if self.exceedsThreshold():
                # gv.tts.speak("     Boat determines threshold to be exceeded.")
                self.updateShore(shoreEntity)
                self.updateBoat(self.currentLocation)
                self.thresholdExceeded = True
        
        # gv.tts.speak("     Boat determines threshold not to be exceeded.")
        #Collects simulation data for UI and collision
        instanceInfo = np.array([self.predictedLocation[0], self.predictedLocation[1], self.locationThreshold[0], self.locationThreshold[1], self.radiusThreshold, self.thresholdExceeded, self.current_model])
        self.thresholdExceeded = False
        # gv.tts.speak("     Boat giving control back to simulation.\n\n")
        return instanceInfo

import models.modelPicker as mp
from haversine import haversine
from collections import deque
import numpy as np

class boatEntity:
    def __init__(self, currentLocation) -> None:
        self.currentLocation = currentLocation
        self.current_index = 0
        self.current_model = mp.modelPicker(currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.currentLocation)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        self.thresholdExceeded = False
        
        #self.last_known_locations = deque(maxlen=10)

    def exceedsThreshold(self) -> bool:
        thresholdPoint = (self.locationThreshold[0], self.locationThreshold[1])
        actualLocationPoint = (self.currentLocation['LAT'], self.currentLocation['LON'])
        predictedPoint = (self.predictedLocation[0], self.predictedLocation[1])
        realDistance = haversine(thresholdPoint, actualLocationPoint)
        predictedDistance = haversine(thresholdPoint, predictedPoint)
        return realDistance > self.radiusThreshold or predictedDistance > self.radiusThreshold

    def updateShore(self, shoreEntity) -> None:
        shoreEntity.recieveLocationUpdate(self.currentLocation)

    def updateBoat(self, currentLocation):
        #print("BOAT: UpdateBoat")
        self.current_model = mp.modelPicker(self.currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.currentLocation)
        self.predictedLocation = (self.currentLocation['LAT'], self.currentLocation['LON'])
        #print("BOAT: new predictedLocation: ", self.predictedLocation[0], self.predictedLocation[1])

    def boatBehaviour(self, currentLocation, shoreEntity):
        self.currentLocation = currentLocation
        self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
     
        if self.exceedsThreshold():
                self.updateShore(shoreEntity)
                self.updateBoat(self.currentLocation)
                self.thresholdExceeded = True
        
        instanceInfo = np.array([self.predictedLocation[0], self.predictedLocation[1], self.locationThreshold, self.radiusThreshold, self.thresholdExceeded, self.current_model])
        self.thresholdExceeded = False
        return instanceInfo

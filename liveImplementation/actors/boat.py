import models.modelPicker as mp
from haversine import haversine
from collections import deque


class boatEntity:
    def __init__(self, currentLocation) -> None:
        self.currentLocation = currentLocation
        self.current_index = 0
        self.current_model = mp.modelPicker(currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.currentLocation)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
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
        #print("BOAT: Excecuting boat behaviour")
        self.currentLocation = currentLocation
        #print("BOAT: Actual position: ", self.currentLocation[2], self.currentLocation[3])
        self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
        #print("BOAT: New Predicted position: ", self.predictedLocation[0], self.predictedLocation[1])

        if self.exceedsThreshold():
                #print("Threshold exceeded")
                self.updateShore(shoreEntity)
                self.updateBoat(self.currentLocation)
        else:
             #print("Threshold not exceeded")
             return
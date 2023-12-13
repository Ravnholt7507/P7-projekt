import models.modelPicker as mp
from haversine import haversine
from collections import deque
import numpy as np
from geopy.distance import geodesic
import globalVariables as gv

class boatEntity:
    def __init__(self, currentLocation) -> None:
        self.last_known_locations = deque(maxlen=10)
        self.last_known_locations.append(dict(currentLocation))

        self.current_index = 0
        self.current_model = mp.modelPicker(self.last_known_locations)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        #print("Predicted_location: ", self.predictedLocation)
        #print("target_location: ", gv.targetValues)
        self.thresholdExceeded = False

    def exceedsThreshold(self) -> bool:
        thresholdPoint = (self.locationThreshold[0], self.locationThreshold[1])
        actualLocationPoint = (self.currentLocation['LAT'], self.currentLocation['LON'])
        predictedPoint = (self.predictedLocation[0], self.predictedLocation[1])
        realDistance = haversine(thresholdPoint, actualLocationPoint)
        predictedDistance = haversine(thresholdPoint, predictedPoint)
        #print("REAL DISTANCE: ", realDistance, predictedDistance, self.current_model)
        #print(realDistance > self.radiusThreshold or predictedDistance > self.radiusThreshold)
        
        return realDistance > self.radiusThreshold or predictedDistance > self.radiusThreshold

    #Sends update to shore when locationThreshold has been exceeded
    def updateShore(self, shoreEntity) -> None:
        shoreEntity.recieveLocationUpdate(self.last_known_locations)

    #Updates internal models of boat when locationThreshold has been exceeded
    def updateBoat(self, currentLocation):
        #("BOAT: UpdateBoat")
        self.last_known_locations.append(dict(currentLocation))
        self.current_model = mp.modelPicker(self.last_known_locations)
        print("Boat queue length", len(self.last_known_locations))
        print("boat: \n", self.last_known_locations)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (self.currentLocation['LAT'], self.currentLocation['LON'])

    #Simulates normal boat behaviour
    def boatBehaviour(self, currentLocation, shoreEntity):
        self.currentLocation = currentLocation
        self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
        if gv.targetValues != 0:
            print("Predicted_location: ", self.predictedLocation)
            print("target_location: ", gv.targetValues)
            # Calculate distance
            distance = geodesic(self.predictedLocation, gv.targetValues).kilometers
            print(f"Distance: {distance} km")
        
        if self.exceedsThreshold():
                self.updateBoat(self.currentLocation)
                self.updateShore(shoreEntity)

                
                self.thresholdExceeded = True
        
        #Collects simulation data for UI and collision
        instanceInfo = np.array([self.predictedLocation[0], self.predictedLocation[1], self.locationThreshold[0], self.locationThreshold[1], self.radiusThreshold, self.thresholdExceeded, self.current_model])
        self.thresholdExceeded = False
        return instanceInfo

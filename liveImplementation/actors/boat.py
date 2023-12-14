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
        self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        #print("Predicted_location: ", self.predictedLocation)
        #print("target_location: ", gv.targetValues)
        self.thresholdExceeded = False

    def exceedsThreshold(self) -> bool:
        actualLocationPoint = (self.currentLocation['LAT'], self.currentLocation['LON'])
        predictedPoint = (self.predictedLocation[0], self.predictedLocation[1])
        realDistance = haversine(predictedPoint, actualLocationPoint)
        print("Distance between actual and predicted: ", realDistance, self.current_model)
        print(self.current_model)
        print(realDistance, self.radiusThreshold)
        return realDistance > self.radiusThreshold

    #Sends update to shore when locationThreshold has been exceeded
    def updateShore(self, shoreEntity) -> None:
        shoreEntity.recieveLocationUpdate(self.last_known_locations)

    #Updates internal models of boat when locationThreshold has been exceeded
    def updateBoat(self, currentLocation):
        #("BOAT: UpdateBoat")
        self.last_known_locations.append(dict(currentLocation))
        self.current_model = mp.modelPicker(self.last_known_locations)
        self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (self.currentLocation['LAT'], self.currentLocation['LON'])

    #Simulates normal boat behaviour
    def boatBehaviour(self, currentLocation, shoreEntity):
        self.currentLocation = currentLocation
        self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
        print("Kørt prediction algorithm")
        print("Predicted location: ", self.predictedLocation)

        if gv.targetValues != 0:
            # Calculate distance
            distance = geodesic(self.predictedLocation, gv.targetValues).kilometers
            print(f"error distance: {distance} km")
        print("LIGE FØR IF, RADIUSTHRES: ", self.radiusThreshold)

        if self.exceedsThreshold():
                print("Determining new threshold")
                self.updateBoat(self.currentLocation)
                self.updateShore(shoreEntity)

                
                self.thresholdExceeded = True
        
        #Collects simulation data for UI and collision
        instanceInfo = np.array([self.predictedLocation[0], self.predictedLocation[1], self.radiusThreshold, self.thresholdExceeded, self.current_model])
        self.thresholdExceeded = False
        return instanceInfo 

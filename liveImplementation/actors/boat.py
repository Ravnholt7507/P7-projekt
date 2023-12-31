import liveImplementation.models.modelPicker as mp
from haversine import haversine
from collections import deque
import numpy as np
from geopy.distance import geodesic
import liveImplementation.settings as s

class boatEntity:
    def __init__(self, currentLocation) -> None:

        self.last_known_locations = deque(maxlen=10)
        self.last_known_locations.append(dict(currentLocation))


        self.current_index = 0
        self.current_model = mp.modelPicker(self.last_known_locations)
        self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        #print("Predicted_location: ", self.predictedLocation)
        #print("target_location: ", s.targetValues)
        self.thresholdExceeded = False

    def exceedsThreshold(self) -> bool:
        actualLocationPoint = (self.currentLocation['LAT'], self.currentLocation['LON'])
        predictedPoint = (self.predictedLocation[0], self.predictedLocation[1])
        realDistance = haversine(predictedPoint, actualLocationPoint)
        #print(f"error distance: {round(realDistance,2)} km")
        return realDistance > self.radiusThreshold

    #Sends update to shore when locationThreshold has been exceeded
    def updateShore(self, shoreEntity) -> None:
        shoreEntity.recieveLocationUpdate(self.last_known_locations)

    #Updates internal models of boat when locationThreshold has been exceeded
    def updateBoat(self, currentLocation):
        #("BOAT: UpdateBoat")
        """ print("\nCurrent Model: ", self.current_model)
        print("Threshold exceed: ")
        print("appending location: ", len(self.last_known_locations)) """
        self.last_known_locations.append(dict(currentLocation)) #Burde måske flyttes til boatBehaviour (og så slet duplicates)
        self.current_model = mp.modelPicker(self.last_known_locations)
        self.radiusThreshold = self.current_model.determineThreshold(self.last_known_locations)
        self.predictedLocation = (self.currentLocation['LAT'], self.currentLocation['LON'])

    #Simulates normal boat behaviour
    def boatBehaviour(self, currentLocation, shoreEntity):
        self.currentLocation = currentLocation
        self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)

        if self.exceedsThreshold():
                self.updateBoat(self.currentLocation)
                self.updateShore(shoreEntity)
                self.thresholdExceeded = True
        else:
            """ print("\nCurrentModel: ", self.current_model)
            print("Threshold NOT exceeded")
            print("appending location: ", len(self.last_known_locations)) """
            self.last_known_locations.append(dict(currentLocation))

        
        #Collects simulation data for UI and collision
        instanceInfo = np.array([self.predictedLocation[0], self.predictedLocation[1], self.radiusThreshold, self.thresholdExceeded, self.current_model])
        self.thresholdExceeded = False
        return instanceInfo 

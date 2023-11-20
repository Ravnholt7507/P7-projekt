from math import radians, sin, cos, sqrt, atan2
import haversine as hv
from haversine import haversine
from geopy.distance import distance

class pointBasedModel:

    def __init__(self, currentLocation) -> None:
        self.thresholdCoordinates = (currentLocation[2], currentLocation[3])
        #return self.determineThreshold(self, currentLocation)

    def determineThreshold(self, currentLocation):
        radiusThreshold = 0.2
        thresholdCoordinates = (currentLocation[2], currentLocation[3])
        return thresholdCoordinates, radiusThreshold
    
    def runPredictionAlgorithm(self):
        return self.thresholdCoordinates
    


class COGBasedModel:
    def __init__(self, currentLocation) -> None:
        return self.determineThreshold(currentLocation)
     
    def determineThreshold(self, currentLocation):
        initialCoordinates = (currentLocation[2],currentLocation[3])
        COG = currentLocation[5]
        radiusThreshold = 0.5
        speed = currentLocation[4] * 1.852
        thresholdCoordinates = distance(kilometers=radiusThreshold).destination(initialCoordinates, COG)
        return thresholdCoordinates, radiusThreshold

    def runPredictionAlgorithm(self):
        return


class vectorBasedModel:
    def __init__(self, currentLocation) -> None:
        return self.determineThreshold(currentLocation)
    

    def determineThreshold(self, currentLocation):
        radiusThreshold = 0.5
        #previousLocation = 
        return radiusThreshold
    
    def runPredictionAlgorithm(self):
        return
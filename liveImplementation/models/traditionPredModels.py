from math import radians, sin, cos, sqrt, atan2
import haversine as hv
from haversine import haversine
from geopy.distance import distance
import globalVariables as globals

class pointBasedModel:

    def __init__(self, currentLocation) -> None:
        self.thresholdCoordinates = (currentLocation[2], currentLocation[3])
        #self.timeIntervals = main.timeIntervals
        #print(self.timeIntervals)
        #return self.determineThreshold(self, currentLocation)

    def determineThreshold(self, currentLocation):
        radiusThreshold = 0.2
        thresholdCoordinates = (currentLocation[2], currentLocation[3])
        return thresholdCoordinates, radiusThreshold
    
    def runPredictionAlgorithm(self, predictedCoordinates):
        return self.thresholdCoordinates
    
class COGBasedModel:
    def __init__(self, currentLocation) -> None:
        print("COGBasedModel: Initializing model")
        self.COG = currentLocation [5]
        self.speed = currentLocation[4] * 1.852
     
    def determineThreshold(self, currentLocation):
        print("COGBasedModel: Determining threshold")
        initialCoordinates = (currentLocation[2],currentLocation[3])
        self.COG = currentLocation[5]
        radiusThreshold = 0.5
        self.speed = currentLocation[4] * 1.852
        thresholdCoordinates = distance(kilometers=radiusThreshold).destination(initialCoordinates, self.COG)
        print("COGBasedModel: Threshold determined as: ", thresholdCoordinates[0], thresholdCoordinates[1])
        return thresholdCoordinates, radiusThreshold

    def runPredictionAlgorithm(self, predictedCoordinates):
        print("COGBasedModel: Running predictionAlgorithm")
        distanceTravelled = self.speed * (globals.timeIntervals / 3600)
        return distance(kilometers=distanceTravelled).destination(predictedCoordinates, self.COG)
    
class vectorBasedModel:
    def __init__(self, currentLocation) -> None:
        self.determineThreshold(currentLocation)
    

    def determineThreshold(self, currentLocation):
        radiusThreshold = 0.5
        #previousLocation = 
        return radiusThreshold
    
    def runPredictionAlgorithm(self):
        return
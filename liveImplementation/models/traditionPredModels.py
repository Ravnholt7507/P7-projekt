from math import radians, sin, cos, sqrt, atan2
import haversine as hv
from haversine import haversine
from geopy.distance import distance
import globalVariables as globals

class pointBasedModel:

    def __init__(self, currentLocation) -> None:
        self.thresholdCoordinates = (currentLocation['LAT'], currentLocation['LON'])
    
    #Defines the behaviour when printing an instance of the class
    def __str__(self):
        return("pointBasedModel")

    #Determines the threshold from which the area that confines the boat is determined
    def determineThreshold(self, lastKnownLocations):
        currentLocation = lastKnownLocations[-1]
        radiusThreshold = 0.2
        thresholdCoordinates = (currentLocation['LAT'], currentLocation['LON'])
        return thresholdCoordinates, radiusThreshold
    
    #Is responsible for the contious estimation of the boat location
    def runPredictionAlgorithm(self, predictedCoordinates):
        return self.thresholdCoordinates
    
class COGBasedModel:
    def __init__(self, lastKnownLocation) -> None:

        self.COG = lastKnownLocation['COG']
        self.speed = lastKnownLocation['SOG'] * 1.852
    
    def __str__(self):
        return("COGBasedModel")
    
    def determineThreshold(self, lastKnownLocations):
        currentLocation = lastKnownLocations[-1]
        #print("COGBasedModel: Determining threshold")
        initialCoordinates = (currentLocation['LAT'],currentLocation['LON'])
        self.COG = currentLocation['COG']
        radiusThreshold = 0.5
        self.speed = currentLocation['SOG'] * 1.852
        thresholdCoordinates = distance(kilometers=radiusThreshold).destination(initialCoordinates, self.COG)
        #print("COGBasedModel: Threshold determined as: ", thresholdCoordinates[0], thresholdCoordinates[1])
        return thresholdCoordinates, radiusThreshold

    def runPredictionAlgorithm(self, predictedCoordinates):
        #print("COGBasedModel: Running predictionAlgorithm")
        distanceTravelled = self.speed * (globals.timeIntervals / 3600)
        return distance(kilometers=distanceTravelled).destination(predictedCoordinates, self.COG)
    
class vectorBasedModel:
    def __init__(self, lastKnownLocations) -> None:
        self.determineThreshold(lastKnownLocations)
    
    def __str__(self):
        return("vectorBasedModel")

    def determineThreshold(self, lastKnownLocations):
        radiusThreshold = 0.5
        #previousLocation = 
        return radiusThreshold
    
    def runPredictionAlgorithm(self):
        return
    
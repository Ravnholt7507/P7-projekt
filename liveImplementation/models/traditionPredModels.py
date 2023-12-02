from math import radians, sin, cos, sqrt, atan2
import haversine as hv
from haversine import haversine
from geopy.distance import distance
from geopy.point import Point
import globalVariables as globals
from geographiclib.geodesic import Geodesic

class pointBasedModel:

    def __init__(self, currentLocation) -> None:
        self.thresholdCoordinates = (currentLocation['LAT'], currentLocation['LON'])
    
    #REPEATING
    #Defines the behaviour when printing an instance of the class
    def __str__(self):
        return("pointBasedModel")

    #REPEATING
    #Determines the threshold from which the area that confines the boat is determined
    def determineThreshold(self, lastKnownLocations):
        currentLocation = lastKnownLocations[-1]
        radiusThreshold = 0.2
        thresholdCoordinates = (currentLocation['LAT'], currentLocation['LON'])
        return thresholdCoordinates, radiusThreshold
    
    #REPEATING
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
        self.radiusThreshold = 0.5
        self.speed = currentLocation['SOG'] * 1.852
        thresholdCoordinates = distance(kilometers=self.radiusThreshold).destination(initialCoordinates, self.COG)
        #print("COGBasedModel: Threshold determined as: ", thresholdCoordinates[0], thresholdCoordinates[1])
        return thresholdCoordinates, self.radiusThreshold

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
        self.radiusThreshold = 0.5
        previousCoordinates = lastKnownLocations[-2]['LAT'], lastKnownLocations[-2]['LON']
        initialCoordinates = lastKnownLocations[-1]['LAT'], lastKnownLocations[-1]['LON']
        self.speed = lastKnownLocations[-1]['SOG'] * 1.852
        #Calculates COG based on two last positions
        COGresult = Geodesic.WGS84.Inverse(previousCoordinates[0], previousCoordinates[1], initialCoordinates[0], initialCoordinates[1])
        self.COG = COGresult['azi1']
        thresholdCoordinates = distance(kilometers=self.radiusThreshold).destination(initialCoordinates, self.COG)
        return thresholdCoordinates, self.radiusThreshold
    
    def runPredictionAlgorithm(self, predictedCoordinates):
        distanceTravelled = self.speed * (globals.timeIntervals / 3600)
        return distance(kilometers=distanceTravelled).destination(predictedCoordinates, self.COG)
    
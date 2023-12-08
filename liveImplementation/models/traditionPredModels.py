from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import math
import sys
sys.path.append('../../P7-projekt')
from ann.Seq2Seq.Models import getModel
import torch 
from sklearn.preprocessing import MinMaxScaler
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
    
class HeadingBasedModel:
    def __init__(self, lastKnownLocation) -> None:
        #if called check heading != 511
        self.Heading = lastKnownLocation['Heading']
        self.speed = lastKnownLocation['SOG'] * 1.852
    
    def __str__(self):
        return("HeadingBasedModel")
    
    def determineThreshold(self, lastKnownLocations):
        if self.Heading != 511:
            currentLocation = lastKnownLocations[-1]
            #print("HeadingBasedModel: Determining threshold")
            initialCoordinates = (currentLocation['LAT'],currentLocation['LON'])
            self.Heading = currentLocation['Heading']
            self.radiusThreshold = 0.5
            self.speed = currentLocation['SOG'] * 1.852
            thresholdCoordinates = distance(kilometers=self.radiusThreshold).destination(initialCoordinates, self.Heading)
            #print("HeadingBasedModel: Threshold determined as: ", thresholdCoordinates[0], thresholdCoordinates[1])
            return thresholdCoordinates, self.radiusThreshold

    def runPredictionAlgorithm(self, predictedCoordinates):
        #print("HeadingBasedModel: Running predictionAlgorithm")
        distanceTravelled = self.speed * (globals.timeIntervals / 3600)
        return distance(kilometers=distanceTravelled).destination(predictedCoordinates, self.Heading)


class AIBasedModel:
    def __init__(self, Queue):
        print("AImodel: Initializing")
        self.model = getModel("Seq2Seq")
        self.model.load_state_dict(torch.load('..\\ann\\saved_models\\Seq2Seq.pth', map_location=torch.device('cpu')))
        self.radiusThreshold = 0.5
        self.Queue = Queue
        self.output = torch.empty((0), dtype=torch.float32) #define placeholder until we get output
        self.timesteps = 0
        self.overshot_timesteps = 0

    def __str__(self):
        return "AImodel"
    
    def normalize(self, tensor):
        scaler = globals.scaler
        tensor = scaler.transform(tensor)
        return torch.from_numpy(tensor)

    def denormalize(self, tensor):
        scaler = globals.scaler
        denorm_tensor = scaler.inverse_transform(tensor)
        return torch.from_numpy(denorm_tensor)

    def remove_gradient(self, tensors):
        return
    
    def percentage(self, whole):
        return math.ceil(float(whole) * 0.1)

    def determineThreshold(self, Queue):
        print("Queue: ")
        self.Queue = Queue
        # Iterate through each dictionary in the deque
        for record in Queue:
            record.pop('MMSI', None)  # Remove 'MMSI', do nothing if the key doesn't exist
            record.pop('BaseDateTime', None)  # Remove 'BaseDateTime', do nothing if the key doesn't exist
            record.pop('VesselName', None)
        

        # Iterate through the deque
        print(len(Queue))

        input = torch.tensor([list(item.values()) for item in Queue])
        input = self.normalize(input)
        input = input.unsqueeze(0)

        #Calculate the needed timesteps
        SOG = Queue[-1]['SOG'] * 1.852
        distanceTime = self.radiusThreshold / SOG
        timesteps = math.floor((distanceTime*60*60) / globals.timeIntervals)
        buffer = self.percentage(timesteps)
        overshot_timesteps = timesteps * 2 + buffer #Overshoots 
        self.timesteps = timesteps
        self.overshot_timesteps = overshot_timesteps

        #Run the model 
        print("WallaWallaWalla", overshot_timesteps+1)
        target = torch.rand(1,overshot_timesteps+1,4) # will change this to only sequence length later
        input = input.type(torch.float32)
        print("input shape: ", input.shape)
        output = self.model(input, target, 0.0)
        output = output.squeeze(0) #Squeeze for at få [1, seq_len,features] = [seq_len, features] , 1 er fra batchsize 
        output = output.cpu().detach().numpy() 
        output = self.denormalize(output)

        thresholdCoordinates = output[timesteps][0], output[timesteps][1]
        self.output = output

        print("HALOOO: ", thresholdCoordinates)
        return thresholdCoordinates, self.radiusThreshold

    def runPredictionAlgorithm(self, predictedCoordinates):
        print("swaaaaaaaaaaaaaaaaaaaaaaaaaag")
        predictedCoordinates = self.output[0][0], self.output[0][1]
        print(self.output[:,0])
        self.output = self.output[1:]
        print(self.output[:,0])
        return predictedCoordinates
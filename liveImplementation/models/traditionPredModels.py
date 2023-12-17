from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from geopy.distance import geodesic
import math
import sys
import time  
sys.path.append('../../P7-projekt')
from ann.Seq2Seq.Models import getModel
import torch 
from sklearn.preprocessing import MinMaxScaler
from collections import deque
import haversine as hv
from haversine import haversine
from geopy.distance import distance
from geopy.point import Point
import globalVariables as globals
from geographiclib.geodesic import Geodesic
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


class pointBasedModel:

    def __init__(self, currentLocation) -> None:
        self.radiusThreshold = 0.05
    
    #REPEATING
    #Defines the behaviour when printing an instance of the class
    def __str__(self):
        return("pointBasedModel")

    #REPEATING
    #Determines the threshold from which the area that confines the boat is determined
    def determineThreshold(self, lastKnownLocations):
        currentLocation = lastKnownLocations[-1]
        self.thresholdCoordinates = (currentLocation['LAT'], currentLocation['LON'])
        return self.radiusThreshold
    
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
        self.COG = currentLocation['COG']
        self.radiusThreshold = 0.057
        self.speed = currentLocation['SOG'] * 1.852
        #print("COGBasedModel: Threshold determined as: ", thresholdCoordinates[0], thresholdCoordinates[1])
        return self.radiusThreshold

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
        return self.radiusThreshold
    
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
            self.Heading = currentLocation['Heading']
            self.radiusThreshold = 0.5
            self.speed = currentLocation['SOG'] * 1.852
            #print("HeadingBasedModel: Threshold determined as: ", thresholdCoordinates[0], thresholdCoordinates[1])
            print ("HALLO", self.radiusThreshold)
            return self.radiusThreshold

    def runPredictionAlgorithm(self, predictedCoordinates):
        #print("HeadingBasedModel: Running predictionAlgorithm")
        distanceTravelled = self.speed * (globals.timeIntervals / 3600)
        return distance(kilometers=distanceTravelled).destination(predictedCoordinates, self.Heading)


class AIBasedModel:
    def __init__(self, Queue):
        self.model = getModel("Seq2Seq")
        self.model.load_state_dict(torch.load('..\\ann\\saved_models\\LSTMSeq2seqAtt.pth', map_location=torch.device('cpu')))
        self.radiusThreshold = 0.1
        self.Queue = Queue
        self.potentialInput = deque(maxlen=10)
        self.input = deque(maxlen=10)
        self.output = torch.empty((0), dtype=torch.float32) #define placeholder until we get output
        self.timesteps = 0

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

    def MakeOutputQueue(self, input):
        for record in input:
            record.pop('MMSI', None)  # Remove 'MMSI', do nothing if the key doesn't exist
            record.pop('BaseDateTime', None)  # Remove 'BaseDateTime', do nothing if the key doesn't exist
            record.pop('Heading', None)

        input = torch.tensor([list(item.values()) for item in input])
        input = self.normalize(input)
        input = input.unsqueeze(0)

        #Run the model 
        input = input.type(torch.float32)
        output = self.model(encoder_inputs = input, prediction_length=40)
        output = output.squeeze(0) #Squeeze for at få [seq_len,features]
        output = output.cpu().detach().numpy() 
        output = self.denormalize(output)

        self.output = output
        return None

    def determineThreshold(self, Queue):
        self.Queue = Queue
        self.input = self.Queue
        self.MakeOutputQueue(self.input)
        return self.radiusThreshold

    def runPredictionAlgorithm(self, predictedCoordinates):

        lat, long = self.output[0][0], self.output[0][1] #lat, long
        CurrentPredictedCoordinates = lat.item(), long.item()

        self.potentialInput.append({f'element_{i}': value.item() for i, value in enumerate(self.output[0])})
        
        self.output = self.output[1:]

        if len(self.output) == 0:
            self.Input = self.potentialInput
            self.MakeOutputQueue(self.input)

            
        return CurrentPredictedCoordinates
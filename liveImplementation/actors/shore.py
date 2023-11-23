import models.modelPicker as mp

class shoreEntity:
    def __init__(self, currentLocation) -> None:
        self.lastKnownLocation = currentLocation
        self.current_model = mp.modelPicker(currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(currentLocation)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        self.updateRecieved = False

    #Updates current knowledge -> is called from boat when locationThreshold has been exceeded
    def recieveLocationUpdate(self, currentLocation):
        self.lastKnownLocation = currentLocation
        self.current_model = mp.modelPicker(currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(currentLocation)
        self.predictedLocation = (currentLocation['LAT'], currentLocation['LON'])
        self.updateRecieved = True

    #Simulates normal shore behaviour
    def shoreBehaviour(self):
        #Are we sure it shouldn't run predictionAlgorithm when updateRecieved == True?
        if self.updateRecieved == False:
            self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
        else:
            self.updateRecieved = False
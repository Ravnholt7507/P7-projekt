import models.modelPicker as mp

class shoreEntity:
    def __init__(self, currentLocation) -> None:
        self.last_known_location = currentLocation
        self.current_model = mp.modelPicker(self.last_known_location)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_location)
        self.predictedLocation = currentLocation
        self.updateRecieved = False


    def recieveLocationUpdate(self, currentLocation):
        self.last_known_location = currentLocation
        self.current_model = mp.modelPicker(self.last_known_location)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(self.last_known_location)
        self.predictedLocation = currentLocation
        self.updateRecieved = True


    def shoreBehaviour(self):
        #Are we sure it shouldn't run predictionAlgorithm when updateRecieved == True?
        if self.updateRecieved == False:
            self.predictedLocation = self.current_model.runPredictionAlgorithm()
        else:
            self.updateRecieved = False
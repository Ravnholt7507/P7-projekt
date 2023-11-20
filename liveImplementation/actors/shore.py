import models.modelPicker as mp

class shoreEntity:
    def __init__(self, currentLocation) -> None:
        self.lastKnownLocation = currentLocation
        self.current_model = mp.modelPicker(currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(currentLocation)
        self.predictedLocation = (currentLocation[2], currentLocation[3])
        self.updateRecieved = False


    def recieveLocationUpdate(self, currentLocation):
        print("SHORE: RecieveLocationUpdate")
        self.lastKnownLocation = currentLocation
        self.current_model = mp.modelPicker(currentLocation)
        self.locationThreshold, self.radiusThreshold = self.current_model.determineThreshold(currentLocation)
        self.predictedLocation = (currentLocation[2], currentLocation[3])
        print("SHORE: New predicted location: ", self.predictedLocation[0], self.predictedLocation[1])
        self.updateRecieved = True
        print("SHORE: Update recieved = True")


    def shoreBehaviour(self):
        print("SHORE: Excecuting shore behaviour")
        #Are we sure it shouldn't run predictionAlgorithm when updateRecieved == True?
        if self.updateRecieved == False:
            print("SHORE:Update recieved == False")
            self.predictedLocation = self.current_model.runPredictionAlgorithm(self.predictedLocation)
            print("SHORE: New predicted location: ", self.predictedLocation[0], self.predictedLocation[1])
        else:
            print("SHORE: UpdateRecieved == True")
            print("SHORE: UpdateRecieved = False")
            self.updateRecieved = False
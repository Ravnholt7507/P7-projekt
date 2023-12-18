import numpy as np
import liveImplementation.settings as s

class simulation:
    def __init__(self, group, shoreEntity, BoatEntity) -> None:
        self.shoreEntity = shoreEntity
        self.boatEntity = BoatEntity
        self.group = group
        self.current_index = 0
        self.completeOutput = np.empty((0, 5))
    
    #Simulates single boat
    def run_simulation(self):
        #While-loop simulates time progression -> run simulation for each instance of the boat
        while self.current_index+1 <= len(self.group):
            # print("\n Interpolated point Point: ", self.current_index)
            instanceOutput = self.boatEntity.boatBehaviour(self.group.iloc[self.current_index], self.shoreEntity)
            s.targetValues = self.group.iloc[self.current_index]['LAT'], self.group.iloc[self.current_index]['LON'] 
            self.shoreEntity.shoreBehaviour()
            self.current_index = self.current_index+1
            self.completeOutput = np.vstack((self.completeOutput, instanceOutput))

        return self.completeOutput
            
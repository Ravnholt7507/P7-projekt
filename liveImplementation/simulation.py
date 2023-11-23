import numpy as np

class simulation:
    def __init__(self, group, shoreEntity, BoatEntity) -> None:
        self.shoreEntity = shoreEntity
        self.boatEntity = BoatEntity
        self.group = group
        self.current_index = 0
        self.completeOutput = np.empty((0, 6))
    
    def run_simulation(self):
        #While-loop simulates time progression
        while self.current_index+1 <= len(self.group):
            instanceOutput = self.boatEntity.boatBehaviour(self.group.iloc[self.current_index], self.shoreEntity)
            self.shoreEntity.shoreBehaviour()
            self.current_index = self.current_index+1
            self.completeOutput = np.vstack((self.completeOutput, instanceOutput))
        
        return self.completeOutput
            
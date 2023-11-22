class simulation:
    def __init__(self, group, shoreEntity, BoatEntity) -> None:
        self.shoreEntity = shoreEntity
        self.boatEntity = BoatEntity
        self.group = group
        self.current_index = 0
    
    def run_simulation(self):
        print("Simulation time ", self.current_index)
        #While-loop simulates time progression
        while self.current_index+1 < len(self.group):
            print("Simulation time ", self.current_index+1)
            self.boatEntity.boatBehaviour(self.group.iloc[self.current_index+1], self.shoreEntity)
            self.shoreEntity.shoreBehaviour()
            self.current_index = self.current_index+1



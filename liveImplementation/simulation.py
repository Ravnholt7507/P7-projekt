class simulation:
    def __init__(self, group, shoreEntity, BoatEntity) -> None:
        self.shoreEntity = shoreEntity
        self.boatEntity = BoatEntity
        self.group = group
        self.current_index = 0
    
    def run_simulation(self):
        #While-loop simulates time progression
        while self.current_index+1 < len(self.group):
            #print("BASETIME: ", self.group.iloc[0][1])
            #print("MMSI: ", self.group.iloc[0][0])
            #print(self.group)
            #print("Simulation time ", self.current_index)
            self.boatEntity.boatBehaviour(self.group.iloc[self.current_index], self.shoreEntity)
            self.shoreEntity.shoreBehaviour()
            self.current_index = self.current_index+1
            
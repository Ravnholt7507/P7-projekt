import numpy as np
import globalVariables as gv

class simulation:
    def __init__(self, group, shoreEntity, BoatEntity) -> None:
        self.shoreEntity = shoreEntity
        self.boatEntity = BoatEntity
        self.group = group
        self.current_index = 0
        self.completeOutput = np.empty((0, 7))
    
    #Simulates single boat
    def run_simulation(self):
        #While-loop simulates time progression -> run simulation for each instance of the boat
        while self.current_index+1 <= len(self.group):
            gv.tts.speak("   Simulating instance {} of {} total instances for current boat:\n", self.current_index+1, len(self.group))
            gv.tts.speak("   Simulation executing boat behaviour:\n")
            instanceOutput = self.boatEntity.boatBehaviour(self.group.iloc[self.current_index], self.shoreEntity)
            gv.tts.speak("   Simulation executing shore behaviour:\n")
            self.shoreEntity.shoreBehaviour()
            self.current_index = self.current_index+1
            gv.tts.speak("   Simulation stacking instance results for current run on the total result array.")
            self.completeOutput = np.vstack((self.completeOutput, instanceOutput))
            gv.tts.speak("   Simulation instance complete. Incrementing time.\n\n")

        gv.tts.speak("Group simulation complete. Returning intermediary output for group.")
        return self.completeOutput
            
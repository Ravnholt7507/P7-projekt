import actors.shore as shore
import actors.boat as boat
import models.traditionPredModels as tradModels
import models.AIPredModels as AIModels
import data.interDataHandler as dataImporter
import simulation as simulationClass

timeIntervals = 10

interpolatedData = dataImporter.cleanseData(timeIntervals)


for name, group in interpolatedData:
    shore_instance = shore.shoreEntity(group.iloc[0])
    boat_instance = boat.boatEntity(group.iloc[0])

    #boat_instance.startSailing(group, shore_instance)

    simulation_instance = simulationClass.simulation(group, shore_instance, boat_instance)
    simulation_instance.run_simulation()



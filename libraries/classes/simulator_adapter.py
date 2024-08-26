# ****************************************************
# Module Purpose:
#   This library defines the Simulator class, which is responsible for interacting with the SUMO Simulator.
#   The Simulator class manages the running of the simulation, from its start to its completion.
#
#
#
# ****************************************************


from libraries.constants import *
from statistics import mean

# These libraries are quite the same. They include most of the commands available in the traci library, but the
# time performance better. Libtraci addresses some limitation of the libsumo library, in particular the multiple client
# communication with the simulation.
import libtraci
import traci.constants as tc
# import libsumo
# import traci

class Simulator:
    configurationPath: str
    logFile: str
    listener: libtraci.StepListener

    def __init__(self,  configurationpath: str, logfile: str):
        self.configurationPath = configurationpath
        self.logFile = logfile
        self.listener = ValueListener()
        libtraci.addStepListener(self.listener)



    def start(self):
        libtraci.start(["sumo", "-c", self.configurationPath + "run.sumocfg"], traceFile=self.logFile)
        print("Note that a simulation step is equivalent to " + str(libtraci.simulation.getDeltaT()) + " seconds")
        # self.oneHourStep()
        self.resume()



    def step(self, quantity=1):
        '''
        This function execute a defined quantity of steps in the simulation (by default only one). Usually one step correspond
        to one second of simulation
        '''
        step = 0
        while step < quantity and self.getRemainingVehicles() > 0:
            libtraci.simulationStep()
            vehiclesSummary = self.getVehiclesSummary()
            print(self.getRemainingVehicles())
            step += 1

    def oneHourStep(self):
        # This is a one-hour single step
        if libtraci.simulation.getMinExpectedNumber() > 0:
            libtraci.simulationStep(3600)

    def resume(self):
        while libtraci.simulation.getMinExpectedNumber() > 0:
            self.step()
        self.end()

    def end(self):
        return libtraci.close()

    def getRemainingVehicles(self):
        # this function returns the vehicles inside the simulation plus the ones that are waiting to start
        return libtraci.simulation.getMinExpectedNumber()


### VEHICLE FUNCTIONS

    def getVehiclesSummary(self):
        vehicleSummary = {}
        vehiclesList = libtraci.vehicle.getIDList()
        summary = []
        if len(vehiclesList) > 1:
            i = 0
            for vehicleID in vehiclesList:
                element = {}
                element["speed"] = libtraci.vehicle.getSpeed(vehicleID)
                element["timeLost"] = libtraci.vehicle.getTimeLoss(vehicleID)
                element["distance"] = libtraci.vehicle.getDistance(vehicleID)
                element["departDelay"] = libtraci.vehicle.getDepartDelay(vehicleID)
                summary.append(element)
                i += 1

            vehicleSummary["averageSpeed"] = mean(element["speed"] for element in summary)
            vehicleSummary["averageTimeLost"] = mean(element["timeLost"] for element in summary)
            vehicleSummary["averageDepartDelay"] = mean(element["departDelay"] for element in summary)
            print("The Average Speed of Vehicles is: " + str(vehicleSummary["averageSpeed"]) + " m/s")
            print("The Average Time lost is " + str(vehicleSummary["averageTimeLost"]) + " seconds")
            return vehicleSummary
        print("There are no vehicles ")
        return None



### INDUCTION LOOP FUNCTIONS

    def getDetectorList(self):
        return libtraci.inductionloop.getIDList()

    def getAverageOccupationTime(self):
        detectorList = self.getDetectorList()
        intervalOccupancies = []
        i = 0
        for detector in detectorList:
            # Although the function for obtaining IDs returns values correctly,
            # once an id is entered for the search, it is not found
            # TODO: find the problem
            intervalOccupancies[i] = libtraci.inductionloop.getIntervalOccupancy(detector)

            i += 1
        average = mean(intervalOccupancies)
        print(average)


class ValueListener(libtraci.StepListener):
    def step(self, t=0):
        # do something after every call to simulationStep
        print("ExampleListener called with parameter %s." % t)
        # Here it is possible to get every kind of info required during onestep.

        # indicate that the step listener should stay active in the next step
        return True

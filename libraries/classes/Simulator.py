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
import os
# These libraries are quite the same. They include most of the commands available in the traci library, but the
# time performance better. Libtraci addresses some limitation of the libsumo library, in particular the multiple client
# communication with the simulation.
import libtraci
import traci.constants as tc
# import libsumo
# import traci

class Simulator:
    configurationPath: str
    routePath: str
    logFile: str
    listener: libtraci.StepListener
    vehicleSummary: {}

    def __init__(self,  configurationpath: str, logfile: str):
        self.configurationPath = configurationpath
        self.routePath = configurationpath
        self.logFile = logfile
        self.listener = ValueListener()
        libtraci.addStepListener(self.listener)

    def start(self):
        if libtraci.simulation.isLoaded():
            print("Warning: there was a previous simulation loaded. It will be overwritten")
        libtraci.start(["sumo", "-c", self.configurationPath + "run.sumocfg"], traceFile=self.logFile)
        print("Note that a simulation step is equivalent to " + str(libtraci.simulation.getDeltaT()) + " seconds")
        #SUBSCRIPTION EXAMPLE
        # self.subscribeToInductionLoop("0.127_2.73_6_1__l0", "vehicleNumber")
        # self.subscribeToInductionLoop("0.127_2.73_6_1__l1", "vehicleNumber")
        # self.subscribeToInductionLoop("0.127_2.73_6_1__l1", "intervalOccupancy")
        self.resume()

    def startBasic(self):
        if libtraci.simulation.isLoaded():
            print("Warning: there was a previous simulation loaded. It will be overwritten")
        libtraci.start(["sumo", "-c", self.configurationPath + "/basic/run.sumocfg"], traceFile=self.logFile)
        self.resume()


    def startCongestioned(self):
        if libtraci.simulation.isLoaded():
            print("Warning: there was a previous simulation loaded. It will be overwritten")
        libtraci.start(["sumo", "-c", self.configurationPath + "/congestioned/run.sumocfg"], traceFile=self.logFile)
        self.resume()

    def step(self, quantity=1):
        '''
        This function execute a defined quantity of steps in the simulation (by default only one). Usually one step correspond
        to one second of simulation
        '''
        step = 0
        while step < quantity and self.getRemainingVehicles() > 0:
            libtraci.simulationStep()
            self.vehiclesSummary = self.getVehiclesSummary()
            self.checkSubscription()
            self.getInductionLoopSummary()
            # self.setTLSProgram("219", "utopia")
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

    def changeRoutePath(self, routePath: str):
        if not os.path.exists(routePath):
            print("Error: the given path does not exists")
            return
        self.routePath = routePath
        os.environ["ROUTEFILENAME"] = routePath
        print("The path was set to " + routePath)

### VEHICLE FUNCTIONS
    def getVehiclesSummary(self):
        vehicleSummary = {}
        vehiclesList = libtraci.vehicle.getIDList()
        summary = []
        if len(vehiclesList) > 1:
            for vehicleID in vehiclesList:
                element = {}
                element["speed"] = libtraci.vehicle.getSpeed(vehicleID)
                element["timeLost"] = libtraci.vehicle.getTimeLoss(vehicleID)
                element["distance"] = libtraci.vehicle.getDistance(vehicleID)
                element["departDelay"] = libtraci.vehicle.getDepartDelay(vehicleID)
                element["totalWaitingTime"] = libtraci.vehicle.getAccumulatedWaitingTime(vehicleID)
                summary.append(element)

            vehicleSummary["averageSpeed"] = mean(element["speed"] for element in summary)
            vehicleSummary["averageTimeLost"] = mean(element["timeLost"] for element in summary)
            vehicleSummary["averageDepartDelay"] = mean(element["departDelay"] for element in summary)
            vehicleSummary["averageWaitingTime"] = mean(element["totalWaitingTime"] for element in summary)
            # print("The Average Speed of Vehicles is: " + str(vehicleSummary["averageSpeed"]) + " m/s.")
            # print("The Average Time lost is " + str(vehicleSummary["averageTimeLost"]) + " seconds.")
            # print("The Average depart delay is " + str(vehicleSummary["averageDepartDelay"]) + " seconds.")
            # print("The Average time waited is " + str(vehicleSummary["averageWaitingTime"]) + " seconds.")
            self.vehicleSummary = vehicleSummary
            return vehicleSummary
        print("There are no vehicles ")
        return None

    # def updateSummary(self):
    #     # Not sure if it's useful include this data inside Simulator class
    #     self.vehicleSummary = self.getVehiclesSummary()

### INDUCTION LOOP FUNCTIONS
    def getDetectorList(self):
        return libtraci.inductionloop.getIDList()

    def getAverageOccupationTime(self):
        detectorList = self.getDetectorList()
        intervalOccupancies = []
        for detector in detectorList:
            intervalOccupancies.append(libtraci.inductionloop.getIntervalOccupancy(detector))
        average = mean(intervalOccupancies)
        # print(average)
        return average

    def getInductionLoopSummary(self):
        detectorList = self.getDetectorList()
        detectors = []
        inductionLoopSummary = {}
        for det in detectorList:
            element = {}
            element["intervalOccupancy"] = libtraci.inductionloop.getIntervalOccupancy(det)
            element["meanSpeed"] = libtraci.inductionloop.getIntervalMeanSpeed(det)
            element["vehicleNumber"] = libtraci.inductionloop.getIntervalVehicleNumber(det)
            detectors.append(element)
        inductionLoopSummary["averageIntervalOccupancy"] = mean(element["intervalOccupancy"] for element in detectors)
        inductionLoopSummary["averageMeanSpeed"] = mean(element["meanSpeed"] for element in detectors)
        inductionLoopSummary["averageVehicleNumber"] = mean(element["vehicleNumber"] for element in detectors)
        return inductionLoopSummary

    def findLinkedTLS(self, detectorID: str):
        lane = libtraci.inductionloop.getLaneID(detectorID)
        tls = self.getTLSList()
        found = []
        for element in tls:
            lanes = libtraci.trafficlight.getControlledLanes(element)
            if lane in lanes:
                found.append(element)

        return found

    def subscribeToInductionLoop(self, inductionLoopID, value: str):
        if value == "intervalOccupancy":
            libtraci.inductionloop.subscribe(inductionLoopID, [libtraci.constants.VAR_INTERVAL_OCCUPANCY])
        elif value == "meanSpeed":
            libtraci.inductionloop.subscribe(inductionLoopID, [libtraci.constants.VAR_INTERVAL_SPEED])
        elif value == "vehicleNumber":
            libtraci.inductionloop.subscribe(inductionLoopID, [libtraci.constants.VAR_INTERVAL_NUMBER])

    def checkSubscription(self):
        results = libtraci.inductionloop.getAllSubscriptionResults()
        for key,value in results.items():
            #checking if vehicle number is high
            if libtraci.constants.VAR_INTERVAL_NUMBER in value and value[libtraci.constants.VAR_INTERVAL_NUMBER] > 10:
                tlsIDs = self.findLinkedTLS(key)
                for element in tlsIDs:
                    self.setTLSProgram(element, "utopia")
                    print("New program is " + str(libtraci.trafficlight.getProgram(element)))
            if libtraci.constants.VAR_INTERVAL_OCCUPANCY in value and value[libtraci.constants.VAR_INTERVAL_OCCUPANCY] > 30:
                print("value in excess")

### TLS FUNCTIONS
    def getTLSList(self):
        return libtraci.trafficlight_getIDList()

    def checkTLS(self, tlsID):
        tls = self.getTLSList()
        if tlsID in tls:
            return True
        else:
            return False

    def setTLSProgram(self, trafficLightID : str, programID: str, all = False):
    ### NOTE: There is still no check of existence of specific program inside the additional file
        if all:
            tls = self.getTLSList()
            for traffic_light in tls:
                libtraci.trafficlight.setProgram(traffic_light, programID)
            print("The program of all traffic lights is changed to" + str(programID))
        elif self.checkTLS(trafficLightID):
            libtraci.trafficlight.setProgram(trafficLightID, programID)
            print("The program of the TLS " + str(trafficLightID) + " is changed to " + str(programID))


class ValueListener(libtraci.StepListener):
    def step(self, t=0):
        # do something after every call to simulationStep
        # print("ExampleListener called with parameter %s." % t)
        # Here it is possible to get every kind of info required during onestep.

        # indicate that the step listener should stay active in the next step
        return True

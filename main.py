import libraries.constants
from libraries.utils.generalUtils import *
from libraries.utils.preprocessingUtils import *
from libraries.classes.DataManager import *
from libraries.classes.Planner import Planner
from libraries.classes.DigitalTwinManager import DigitalTwinManager
from libraries.classes.Agent import *
from libraries.classes.SumoSimulator import Simulator
from libraries.classes.SubscriptionManager import QuantumLeapManager
from libraries.classes.Broker import Broker
from libraries.classes.TrafficModeler import TrafficModeler
from mobilityvenv.MobilityVirtualEnvironment import setupPhysicalSystem, startPhysicalSystem
from data.preprocessing import preprocessingSetup

if __name__ == "__main__":

    configurationPath = SUMO_PATH
    logFile = "./command_log.txt"
    sumoSimulator = Simulator(configurationPath=configurationPath, logFile=logFile)
    model = TrafficModeler(simulator=sumoSimulator, trafficDataFile=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, sumoNetFile=SUMO_NET_PATH,
                           date='2024-02-01', timeSlot='07:00-08:00', modelType='underwood')
    model.saveTrafficData()
    generateFlow(inputFilePath=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, modelFilePath=MODEL_DATA_FILE_PATH,
                 outputFilePath=FLOW_DATA_FILE_PATH, date='2024-02-01',
                 timeSlot='07:00-08:00')
    model.vTypeGeneration(modelType='idm')
    model.generateRandomRoute(sumoNetPath=libraries.constants.SUMO_NET_PATH,
                              outputRoutePath=SUMO_PATH)
    model.generateRoute()

    model.plotModel()

    # 0. Pre-processing phase (to be run only once)
    preprocessingSetup.run()

    model = TrafficModeler(trafficDataFile=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, sumoNetFile=SUMO_NET_PATH,
                           date='2024-02-01', timeSlot='00:00-23:00', modelType='underwood')
    model.generateRandomRoute(sumoNetPath=libraries.constants.SUMO_NET_PATH, outputRoutePath=SUMO_PATH + '/sampleRoutes.rou.xml')
    model.saveTrafficData()
    model.plotModel()

    # 1. Instantiate Orion CB, IoT Agent and create three types of subscriptions.
    envVar = loadEnvVar(CONTAINER_ENV_FILE_PATH)
    iotanorth = envVar.get("IOTA_NORTH_PORT")
    iotasouth = envVar.get("IOTA_SOUTH_PORT")
    cbport = envVar.get("ORIONLD_PORT")
    timescalePort = envVar.get("TIMESCALE_DB_PORT")
    quantumleapPort = envVar.get("QUANTUMLEAP_PORT")
    contextBroker = Broker(pn=cbport, pnt=None, host="localhost", fiwareservice="openiot")
    cbConnection = contextBroker.createConnection()
    IoTAgent = Agent(aid="01", hostname="localhost", cb_port=cbport, south_port=iotasouth, northport=iotanorth, fw_service="openiot", fw_path="/")
    quantumLeapManager = QuantumLeapManager(containerName="fiware-quantumleap", cbPort=cbport, quantumleapPort=quantumleapPort)

    quantumLeapManager.createQuantumLeapSubscription(cbConnection=cbConnection, entityType="Road Segment", attribute="trafficFlow", description="Notify me of Traffic Flow")
    quantumLeapManager.createQuantumLeapSubscription(cbConnection=cbConnection, entityType="trafficflowobserved", attribute="trafficFlow", description="Notify me of Traffic Flow")
    quantumLeapManager.createQuantumLeapSubscription(cbConnection=cbConnection, entityType="Device", attribute="trafficFlow", description="Notify me of traffic Flow")


    #### Comment/decomment these two code lines to run the physical system.
    # TODO: thread-multiprocessing
    roads, files = setupPhysicalSystem(IoTAgent)
    startPhysicalSystem(roads)

    # 2. The DigitalTwinManager needs i) a DataManager for accessing data; ii) a SumoSimulator for running simulations
    #    iii) a Planner including a ScenarioGenerator for generating sumoenv scenarios.
    timescaleManager = TimescaleManager(
        host="localhost",
        port=timescalePort,
        dbname="quantumleap",
        username="postgres",
        password="postgres"
    )
    dataManager = DataManager("TwinDataManager")
    dataManager.addDBManager(timescaleManager)

    configurationPath = SUMO_PATH
    logFile = "./command_log.txt"
    sumoSimulator = Simulator(configurationPath=configurationPath, logFile=logFile)
    twinPlanner = Planner(simulator=sumoSimulator)
    twinManager = DigitalTwinManager(dataManager, configurationPath, logFile)

    # 3. Simulation of one hour slot scenario. The function will open sumo gui. The play button must be pressed to run the simulation. When simulation ends, the function returns the folder path in which sumoenv files have been generated.
    scenarioFolder = twinManager.simulateBasicScenarioForOneHourSlot(timeslot="00:00-01:00", date="2024/02/01", entityType='Road Segment', totalVehicles=100, minLoops=3, congestioned=False, activeGui=True, timecolumn="timeslot")
    print(scenarioFolder)
    twinManager.generateGraphs(scenarioFolder)
    twinManager.showGraphs(scenarioFolder, saveSummary=False)




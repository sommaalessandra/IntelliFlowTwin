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

### TODO: Rearrangement of project functions and modules -> delete main and instead create functions on web app
def configureCalibrateAndRun(dataFilePath: str, carFollowingModel: str, macroModelType: str, tau: str,
                             parameters: {}, date: str, timeslot: [], edge_id: str):

    configurationPath = SUMO_PATH + "/standalone"
    logFile = "./command_log.txt"
    sumoSimulator = Simulator(configurationPath=configurationPath, logFile=logFile)
    print("Instantiating a Traffic Modeler...")
    basemodel = TrafficModeler(simulator=sumoSimulator, trafficDataFile=dataFilePath,
                               sumoNetFile=SUMO_NET_PATH,
                               date=date,
                               timeSlot='00:00-01:00',
                               modelType=macroModelType)
    print("Starting Configuration")
    for hour in range(timeslot[0], timeslot[1]):
        if hour < 9:
            basemodel = TrafficModeler(simulator=sumoSimulator, trafficDataFile=dataFilePath,
                                   sumoNetFile=SUMO_NET_PATH,
                                   date=date,
                                   timeSlot='0' + str(hour) + ':00-' + '0' + str(hour + 1) + ':00',
                                   modelType=macroModelType)
        elif hour == 9:
            basemodel = TrafficModeler(simulator=sumoSimulator, trafficDataFile=dataFilePath,
                                   sumoNetFile=SUMO_NET_PATH,
                                   date=date, timeSlot='0' + str(hour) + ':00-' + str(hour + 1) + ':00',
                                   modelType=macroModelType)
        else:
            basemodel = TrafficModeler(simulator=sumoSimulator, trafficDataFile=dataFilePath,
                                   sumoNetFile=SUMO_NET_PATH,
                                   date=date, timeSlot=str(hour) + ':00-' + str(hour + 1) + ':00',
                                   modelType=macroModelType)
        typeFilePath, confPath = basemodel.vTypeGeneration(modelType=carFollowingModel, tau=tau,
                                                       additionalParam=parameters)
        basemodel.saveTrafficData(outputDataPath=typeFilePath + "/model.csv")
        basemodel.runSimulation(withGui=True)
    confPath = projectPath + "/" + confPath
    basemodel.evaluateModel(edge_id=edge_id, confPath=confPath, outputFilePath=confPath + "/detectedFlow.csv")
    basemodel.evaluateError(detectedFlowPath=confPath + "/detectedFlow.csv", outputFilePath=confPath + "/error_summary.csv")
    basemodel.plotTemporalResults(resultFilePath=confPath + "/detectedFlow.csv", showImage=False)
    return confPath

if __name__ == "__main__":


    ### Instantiate a Trafic Modeler, specifing which macromodel you want to use to get the missing data (speed, density, etc.)
    configurationPath = SUMO_PATH + "/standalone"
    logFile = "./command_log.txt"
    # sumoSimulator = Simulator(configurationPath=configurationPath, logFile=logFile)

    # getAverageEdgeLength(sumoNetFile=SUMO_NET_PATH)
    # model = TrafficModeler(simulator=sumoSimulator, trafficDataFile="data/processed_traffic_flow.csv", sumoNetFile=SUMO_NET_PATH,
    #                            date='2024-02-01', timeSlot='15:00-16:00', modelType='vanaerde')
    ### Loop for simulating a day
    macroModelType = "underwood"
    carFollowingModel = "W99"

    # configureCalibrateAndRun(dataFilePath=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, carFollowingModel='W99',
    #                                    macroModelType="underwood", tau="1", parameters={"cc1": "1.5", "cc2": "10.0"},
    #                                    date='2024-02-01', timeslot=[0,1], edge_id='23288872#4')
    # for timeslot in range(0, 24):
    #     if timeslot < 9:
    #         model = TrafficModeler(simulator=sumoSimulator, trafficDataFile=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH,
    #                                sumoNetFile=SUMO_NET_PATH,
    #                                date='2024-02-01',
    #                                timeSlot='0' + str(timeslot) + ':00-' + '0' + str(timeslot + 1) + ':00',
    #                                modelType=macroModelType)
    #     elif timeslot == 9:
    #         model = TrafficModeler(simulator=sumoSimulator, trafficDataFile=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH,
    #                                sumoNetFile=SUMO_NET_PATH,
    #                                date='2024-02-01', timeSlot='0' + str(timeslot) + ':00-' + str(timeslot + 1) + ':00',
    #                                modelType=macroModelType)
    #     else:
    #         model = TrafficModeler(simulator=sumoSimulator, trafficDataFile=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH,
    #                                sumoNetFile=SUMO_NET_PATH,
    #                                date='2024-02-01', timeSlot=str(timeslot) + ':00-' + str(timeslot + 1) + ':00',
    #                                modelType=macroModelType)
        # typeFilePath, confPath = model.vTypeGeneration(modelType=carFollowingModel, tau="1",
        #                                                additionalParam={"sigma": "0", "sigmaStep": "0.5"})
        # typeFilePath, confPath = model.vTypeGeneration(modelType='IDM', tau="1.5", additionalParam={"delta": "6","stepping": "0.1"})
        # typeFilePath, confPath = model.vTypeGeneration(modelType='W99', tau="1", additionalParam={"cc1": "1.5", "cc2": "10.0"})
        # model.saveTrafficData(outputDataPath=typeFilePath + "/model.csv")
        # model.runSimulation(withGui=False)

    # ### GENERATE flow.csv FILE TO BE FED INTO edgeDataFromFlow.py script to get edgedata.xml
    # generateFlow(inputFilePath=PROCESSED_TRAFFIC_FLOW_EDGE_FILE_PATH, modelFilePath=MODEL_DATA_FILE_PATH,
    #              outputFilePath=FLOW_DATA_FILE_PATH, date='2024-02-01',
    #              timeSlot='00:00-01:00')
    # ### GENERATE edgefile.xml TO BE USED BY routeSampler.py script to generate
    # generateEdgeFromFlow(inputFlowPath=FLOW_DATA_FILE_PATH, detectorFilePath=SUMO_DETECTORS_ADD_FILE_PATH,
    #                      outputEdgePath=EDGE_DATA_FILE_PATH)

    ### Micro-model generation. The given typeFilePath output is the specific experiment folder
    ### Uncomment the model you want to generate and calibrate the parameters
    ###KRAUSS
    # typeFilePath, confPath = model.vTypeGeneration(modelType='Krauss', tau="1", additionalParam={"sigma": "0", "sigmaStep": "0.5"})
    ###EIDM
    # typeFilePath, confPath = model.vTypeGeneration(modelType='IDM', tau="1", additionalParam={"delta": "4","stepping": "0.25"})
    ###W99
    # typeFilePath, confPath = model.vTypeGeneration(modelType='W99', tau="1", additionalParam={"cc1": "1.30","cc2": "8.0"})
    # model.saveTrafficData(outputDataPath=typeFilePath + "/model.csv")

    ### THIS FUNCTION GENERATES ROUTE FILE ACCORDING TO FLOW randomTrips.py + routeSampler.py .
    ### IT TAKES LONG TIME TO BE COMPLETED SO CONSIDER TO RUN IT ONLY ONCE
    # model.generateRoute(inputEdgePath=EDGE_DATA_FILE_PATH, withInitialRoute=True, useStandardRandomRoute=False)
    # model.runSimulation()

    ### Evaluate model according to detector output afte SUMO simulation. It generates a .csv output file too, including
    ### speed and flow differences

    # model.evaluateModel(edge_id='23288872#4', confPath= confPath, outputFilePath= confPath + "/detectedFlow.csv")
    # model.evaluateModelwithDetector(detectorFilePath="sumoenv/static/detectors.add.xml", detectorOutputSUMO="sumoenv/output/detector.out.xml",
    #                                 outputFilePath= typeFilePath + "/output/detectedFlow.csv")
    # model.evaluateError(detectedFlowPath= confPath + "/detectedFlow.csv", outputFilePath=confPath + "/error_summary.csv")

    ### If you include a result, it will plot simulation detected data, otherwise will plot macroscopic derived data (the model one)
    # model.plotModel(result=None)
    # model.plotTemporalResults(resultFilePath=confPath + "/detectedFlow.csv", showImage=True)
    # model.compareResults(resultFilePath='sumoenv/greenshield_krauss_t15.csv')
    # model.plotModel(result="data/detectedFlow.csv")

    # 0. Pre-processing phase (to be run only once)
    # preprocessingSetup.run()

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




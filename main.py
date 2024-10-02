import multiprocessing
from ngsildclient import Client, SubscriptionBuilder
import physical_system_startup
from libraries.classes.Simulator import Simulator
from libraries.constants import *
from libraries.general_utils import *
from libraries.preprocessing_utils import *
from libraries.classes.Agent import *
from libraries.classes.Planner import *
from physical_system_startup import *
from libraries.constants import roadSegmentType

if __name__ == "__main__":

    # After running the platform's containers, a client is instantiated to connect to Orion CB
    envVar = loadEnvVar(containerEnvPath)
    cbport = envVar.get("ORIONLD_PORT")
    iotanorth = envVar.get("IOTA_NORTH_PORT")
    iotasouth = envVar.get("IOTA_SOUTH_PORT")
    orion = Client(hostname="localhost", port=1026, tenant="openiot", overwrite=True)
    IoTAgent = Agent(aid="01", hostname="localhost", cb_port=cbport, south_port=iotasouth, northport=iotanorth, fw_service="openiot",
                     fw_path="/")

    # payload = SubscriptionBuilder("http://fiware-quantumleap:8668/v2/notify").description(
    #      "Notify me of traffic Flow ").select_type(roadSegmentType).watch(["trafficFlow"]).build()
    payload = SubscriptionBuilder("http://fiware-quantumleap:8668/v2/notify").description(
        "Notify me of traffic Flow ").select_type("Device").watch(["trafficFlow"]).build()
    print(payload)
    subscr_id = orion.subscriptions.create(payload)

    roads, files = setupPhysicalSystem(IoTAgent)
    startPhysicalSystem(roads)

    # simulation = Simulator(configurationpath=simulationPath, logfile="./command_log.txt")
    # simulation.startBasic()
    # simulation.start()

    simulator = Simulator(configurationpath="SUMO/joined/", logfile="./command_log.txt")
    simulator.getInductionLoopSummary()
    planner = Planner(connectionString="postgres://postgres:postgres@localhost:5432/quantumleap", sim=simulator, agent=IoTAgent)

    planner.recordFlow(timeslot="01:00-02:00", date="2024/02/01", devicetype='roadsegment', timecolumn="datetime")

    filePath = planner.scenarioGenerator.generateRoutes("libraries/edgefile.xml", 3000, 3, congestioned=True)
    planner.scenarioGenerator.setScenario(routeFilePath=filePath, manual=False)
    # simulator.changeRoutePath("SUMO/joined/2024-09-23_15-05-52_congestioned/generatedRoutes.rou.xml")

    # simulator = Simulator(configurationpath=simulationPath, logfile="./command_log.txt")
    # simulator.startBasic()
    simulator.start()


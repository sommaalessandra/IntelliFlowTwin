import multiprocessing
from ngsildclient import Client, SubscriptionBuilder
import physical_system_startup
from libraries.classes.Simulator import Simulator
from libraries.constants import *
from libraries.general_utils import *
from libraries.preprocessing_utils import *
from libraries.classes.Agent import *
from physical_system_startup import *

if __name__ == "__main__":

    ### PREPROCESSING PHASE
    # #csv file to be filtered
    # inputFile = simulationDataPath + 'traffic_flow_2024.csv'
    # filterFile = simulationDataPath + 'roadnames.csv'  # File CSV contenente l'insieme dei nomi di vie
    # outputFile = simulationDataPath + 'output.csv'  # File CSV dove salvare il risultato filtrato
    # accuracyFile = simulationDataPath + 'accuratezza-spire-anno-2024.csv'  # File che rappresenta in percentuale l'accuratezza delle spire
    # accuracyOutputFile = simulationDataPath + 'accurate_output.csv'
    #
    # # First the entries are filtered based on the accuracy value of measurement
    # filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accuracyOutputFile, accepted_percentage=95)
    # # call this function to filter road according to the filter file
    # filter_roads(accuracyOutputFile, filterFile, outputFile)
    # # this function add a new column in the data, pointing which edge_id is linked with the referring roads
    # link_roads_IDs(outputFile, filterFile)
    #
    # linked_roads = simulationDataPath + 'final.csv'
    # generate_edgedata_file(linked_roads, 'edgedata.xml', '01/03/2024', '10:00-11:00')
    #
    # filter_day(linked_roads)

    # After running the platform's containers, a client is instantiated to connect to Orion CB


    #
    envVar = loadEnvVar(containerEnvPath)
    cbport = envVar.get("ORIONLD_PORT")
    iotanorth = envVar.get("IOTA_NORTH_PORT")
    iotasouth = envVar.get("IOTA_SOUTH_PORT")
    orion = Client(hostname="localhost", port=1026, tenant="openiot", overwrite=True)
    IoTAgent = Agent(aid="01", hostname="localhost", cb_port=cbport, south_port=iotasouth, northport=iotanorth, fw_service="openiot",
                     fw_path="/")

    payload = SubscriptionBuilder("http://fiware-quantumleap:8668/v2/notify").description(
        "Notify me of traffic Flow ").select_type("Device").watch(["trafficFlow"]).build()
    print(payload)
    subscr_id = orion.subscriptions.create(payload)

    roads, files = setupPhysicalSystem(IoTAgent)
    startPhysicalSystem(roads)

    # simulation = Simulator(configurationpath=simulationPath, logfile="./command_log.txt")
    # simulation.startBasic()
    # simulation.start()




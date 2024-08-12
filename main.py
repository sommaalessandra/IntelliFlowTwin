import multiprocessing
from ngsildclient import Client
import physical_system_startup
from libraries.constants import *
from libraries.general_utils import *
from libraries.preprocessing_utils import *
from libraries.classes.iotagent_adapter import *
from physical_system_startup import *

if __name__ == "__main__":

    ### PREPROCESSING PHASE
    # #csv file to be filtered
    # inputFile = simulationPath + 'traffic_flow_2024.csv'
    # filterFile = simulationPath + 'roadnames.csv'  # File CSV contenente l'insieme dei nomi di vie
    # outputFile = simulationPath + 'output.csv'  # File CSV dove salvare il risultato filtrato
    # accuracyFile = simulationPath + 'accuratezza-spire-anno-2024.csv'  # File che rappresenta in percentuale l'accuratezza delle spire
    # accuracyOutputFile = simulationPath + 'accurate_output.csv'
    #
    # # First the entries are filtered based on the accuracy value of measurement
    # filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accuracyOutputFile, accepted_percentage=95)
    # # call this function to filter road according to the filter file
    # filter_roads(accuracyOutputFile, filterFile, outputFile)
    # # this function add a new column in the data, pointing which edge_id is linked with the referring roads
    # link_roads_IDs(outputFile, filterFile)
    #
    # linked_roads = simulationPath + 'final.csv'
    # generate_edgedata_file(linked_roads, 'edgedata.xml', '01/03/2024', '20:00-21:00')
    #
    # filter_day(linked_roads)

    # After running the platform's containers, a client is instantiated to connect to Orion CB

    envVar = loadEnvVar(containerEnvPath)
    cbport = envVar.get("ORIONLD_PORT")
    iotanorth = envVar.get("IOTA_NORTH_PORT")
    iotasouth = envVar.get("IOTA_SOUTH_PORT")
    orion = Client(hostname="localhost", port=1026, tenant="openiot", overwrite=True)
    IoTAgent = Agent(aid="01", cb_port=cbport, south_port=iotasouth, northport=iotanorth, fw_service="openiot",
                     fw_path="/")

    roads, files = setupPhysicalSystem(IoTAgent)
    startPhysicalSystem(roads)

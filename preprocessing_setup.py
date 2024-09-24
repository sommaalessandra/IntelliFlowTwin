from libraries.constants import *
from libraries.preprocessing_utils import *

### PREPROCESSING PHASE
#csv file to be filtered
inputFile = simulationDataPath + 'traffic_flow_2024.csv'  # File CSV contenente l'insieme dei nomi di vie
outputFile = simulationDataPath + 'output.csv'  # File CSV dove salvare il risultato filtrato
accuracyFile = simulationDataPath + 'accuratezza-spire-anno-2024.csv'  # File che rappresenta in percentuale l'accuratezza delle spire
accuracyOutputFile = simulationDataPath + 'accurate_output.csv'
filterFile = simulationPath + 'roadnames.csv'

# First the entries are filtered based on the accuracy value of measurement
filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accuracyOutputFile, accepted_percentage=95)
# call this function to filter road according to the filter file
filter_roads(accuracyOutputFile, filterFile, outputFile)
# this function add a new column in the data, pointing which edge_id is linked with the referring roads
link_roads_IDs(outputFile, filterFile)

linked_roads = simulationDataPath + 'final.csv'
generate_edgedata_file(linked_roads, 'edgedata.xml', '01/03/2024', '10:00-11:00')

filter_day(linked_roads)
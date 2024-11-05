import os
from libraries.utils.preprocessing_utils import *

#csv file to be filtered
inputFile = (simulationDataPath + 'traffic_flow_2024.csv')
accuracyFile = simulationDataPath + 'accuratezza-spire-anno-2024.csv'
accurateInputFile = simulationDataPath + 'accurate_traffic_flow.csv'
netFile = simulationPath + "static/joined_lanes.net.xml"
processedTrafficFlow = simulationDataPath + 'processed_traffic_flow.csv'

filter_for_shadow_manager(processedTrafficFlow)
filter_with_accuracy(inputFile, accuracyFile, date_column='data', sensor_id_column='codice_spira', output_file=accurateInputFile, accepted_percentage=95)
generate_roadnames_file(inputFile=accurateInputFile, sumoNetFile=netFile, outputFile='roadnames.csv')
roadnamesFile = os.path.abspath(simulationDataPath + 'roadnames.csv')
fill_missing_edge_id(roadnamesFile)
link_edge_id(inputFile=accurateInputFile, roadnameFile=roadnamesFile, outputFile=processedTrafficFlow)

generate_edgedata_file(processedTrafficFlow, 'edgedata.xml', '01/02/2024', '07:00-08:00')
filter_day(processedTrafficFlow, date='01/02/2024')

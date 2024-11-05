# Pre-processing
## Data Files
This section describes the input and output files used within the preprocessing phase. Some files are the result of a preprocessing activity but are later used as input for other functions. Therefore, these files are reported in the Input/Output section.
### Input Files
- **traffic_flow_2024.csv**: this file contains the traffic loop measurement data from January to April 2024. This data was taken from the [Bologna Open Data Repository - Traffic FLow](https://opendata.comune.bologna.it/explore/dataset/rilevazione-flusso-veicoli-tramite-spire-anno-2024). Used in:
	- *filterWithAccuracy*: using this file with *accuratezza-spire-anno-2024.csv*, the function filters the file, keeping the entries that have at least an certain amount of accuracy in percentage (above 95% by default). The output file is *accurate_traffic_flow.csv*.
	
- **accuratezza-spire-anno-2024.csv**: this file reports the accuracy value, in percentage related to the measurement taken. This data was taken from the [Bologna Open Data Repository - Traffic Flow Accuracy](https://opendata.comune.bologna.it/explore/dataset/accuratezza-spire-anno-2024). Used in:
	- *filterWithAccuracy*: description given above

### Output Files
- **processed_traffic_flow.csv**: this file contains the accurate traffic loop measurement augmented with the road edge IDs coupled with the SUMO net. This is the outcome of an accuracy filtering and a linking function for edge_IDs.

### Input/Output Files 
- **accurate_traffic_flow.csv**: this file is the outcome of the *filter_with_accuracy* function. It contains the traffic loop measurement from January to April 2024 that have a certain value of accuracy (above 95% by default). Used in:
	- *(LEGACY) generate_detector_csv*: (INCLUDED into generate_roadname_file) function that creates a *detector.add.xml* file useful for simulate traffic loops inside the SUMO net.
	- *generate_roadname_file*: the function generate a *roadnames.csv*, a file that links each road to the SUMO net. It also generate a *detectors.add.xml*, an additional file for SUMO that simulate the traffic loops inside the SUMO net.
	- *link_edge_id*: using this file and the *roadnames.csv* file created previously, this function add the edge id columns inside the file, creating *linked_traffic_flow.csv*, file that can be used for generating counting/flow data for SUMO simulation.
- **roadnames.csv**: this file is the outcome of the *generate_roadname_file* function. It contains the name, the geopoint and the edge id for each road, linking the roads to the edges in the SUMO net. Used in:
	- *fill_missing_edge_id*: the function finds entries that didn't find any match in the *generate_roadname_file* and add the first edge id found with the same road name.
	- *link_edge_id*: description given above.
## Pre-processing flow
The following are in the execution order all the operations that were performed in the pre-processing activity.
- **filterWithAccuracy**: the traffic loop measurement (*traffic_flow_2024*) file is first filtered according to the accuracy value (reported as a percentage value). The file used to filter by accuracy is *accuratezza-spire-anno-2024.csv*. The result of this operation is saved in *accurate_traffic_flow.csv*
- **generateRoadnamesFile**: the result of this filtering is used, together with the SUMO map (*joined_lanes.net.xml*), to generate *roadnames.csv*, a file that links each traffic loop to an edge of the network in SUMO. In addition, this function also generates the *detector.add.xml* file, which allows the traffic loops to be represented within the SUMO network.
- **linkEdgeId**: using the accuracy-filtered file (*accurate_traffic_flow*), together with the roads file generated earlier (*roadnames*), through this function we augment the measurement data, associating each measurement with the edge Id of the map in SUMO. The result of this operation is saved in *processed_traffic_flow.csv*. Clearly the augmenting of the data is not direct, but passes through roadnames file for reasons of computational complexity reasons.
- **generateEdgeDataFile**: the now-refined file can be used for generating the car count file, named *edgedata.xml* .  Through this function, a date and time slot is chosen, and the appropriate file is generated, which is used for route generation within the SUMO simulator (through routeSampler.py script, available in SUMO tools).

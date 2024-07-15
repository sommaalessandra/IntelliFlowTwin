# Urban Simulation with SUMO 

## Bologna Districts Case Study
TODO: explain briefly the case study 
## Data Sourcing  
In order to construct a plausible simulation scenario, it was necessary to obtain data for the construction of the road network in SUMO (consisting of roads, junctions, traffic lights, etc.) and the traffic data itself. 

As for road networks, configurations available in the SUMO scenario repository were used (available here https://github.com/DLR-TS/sumo-scenarios/tree/main). The repository provides two neighbourhoods of the city of Bologna, identified by the name of their main street, namely Costa and Pasubio. These two areas are also proposed in joint form in the folder named *joined*. The folder consists of the network file (with the *net.xml* extension) and several additional files that enrich and complete the simulation environment:
- **run.sumocfg**: simulations on SUMO are usually defined via the .sumocfg file, which specifies what the inputs and outputs of the simulation are. In addition, there are parameters that modify the execution of the simulation itself (e.g. microscopic or mesoscopic execution).
- **joined_buslanes.net.xml**: a SUMO network file that describes the traffic-related part of a map, the roads and intersections the simulated vehicles run along or across. The SUMO network contains every street (as a collection of lanes) including position, shape and speed limit of every lane, all the junctions and connections between lanes and junctions. 
- **routesampled.rou.xml**: this file represents the set of vehicles and routes they will take within the simulation. This data is the result of a series of pre-processing operations which, starting from the traffic loop readings obtained from Open Data, generated vehicle routes that would comply with the data detected. Details on how these routes are generated are explained in the pre-processing section.
- **joined_tls.add.xml** : the file includes the set of traffic lights and defines their operating logic
- **joined_vtypes_add.xml** : The file includes the set of vehicle types passing through the simulation. Each vehicle is characterised by its size, the shape it takes in the simulation, acceleration and braking values
- **tripinfos.xml**: output file #TODO

All files presented are used within the simulation thanks to the configuration file *.sumocfg*. Once the simulation has started, the user must wait for it to complete in order to collect the output data.

The traffic data were taken from the Open Data database of the municipality of Bologna.

## Set-up of the Simulation and data pre-processing 

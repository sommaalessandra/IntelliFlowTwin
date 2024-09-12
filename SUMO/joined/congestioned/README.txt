This is simulation is made with the following commands:

###For generating a first route to use next:
python randomTrips.py -n .\joined_lanes.net.xml -r sampleRoutes.rou.xml --fringe-factor 10 

### Route Generator - 3000 vehicles with a path passing through at least 3 traffic loops:
routeSampler.py -r .\sampleRoutes.rou.xml --edgedata-files .\edgedata.xml -o generatedRoutes.rou.xml --total-count 3000 --optimize full --min-count 3

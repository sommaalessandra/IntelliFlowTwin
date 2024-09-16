import time

import pandas as pd
from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.classes.Broker import Broker
from typing import List
from libraries.constants import shadowPath
from ngsildclient import CORE_CONTEXT, Entity, Rel
from geojson import Point
#import json
import random
from datetime import datetime, timedelta
from libraries.general_utils import convertDate



device_id = "TL451"
time_slot = "00:00-01:00"
traffic_flow = 78 # Example traffic flow count
coordinates : List[float] = [44.5123626162894, 11.287461221671]
lane_direction = "NO"  # Example lane direction
date = "01/02/2024"

shadow_manager = DigitalShadowManager()
roadShadow =shadow_manager.searchShadow(shadowType="road",timeSlot=time_slot,trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction, deviceID=device_id)
roadName = roadShadow.name
edgeID = roadShadow.get('edgeID')
startPoint = roadShadow.get('startPoint')
endPoint = roadShadow.get('endPoint')
trafficLoopShadow = shadow_manager.searchShadow(shadowType="trafficLoop",timeSlot=time_slot,trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction, deviceID=device_id)
loopCode=trafficLoopShadow.get("loopCode")
loopLevel=trafficLoopShadow.get("loopLevel")


print(roadName, edgeID)
print(loopCode, loopLevel)


#entities = client.query(type="AirQualityObserved", q="NO2>40")
# restart from HERE --> create an example road entity and query it

transportationContext= ["https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/4df15072b13da6c7bd7e86915df91fb28921aa7f/context.jsonld",CORE_CONTEXT]
deviceContext = ["https://raw.githubusercontent.com/smart-data-models/dataModel.Device/master/context.jsonld", CORE_CONTEXT]


# static context example
roadNumber = 1
roadID = 'R{:03d}'.format(roadNumber)
road = Entity("Road", roadID, ctx=transportationContext)
road.prop('alternateName', roadName)




[longitude, latitude] = roadShadow.get('coordinates')

roadSegmentNumber = 1
roadSegmentID = 'RS{:03d}'.format(roadSegmentNumber)
roadSegment = Entity("RoadSegment", roadSegmentID, ctx=transportationContext)

roadSegment.prop('startPoint', int(startPoint))
roadSegment.prop('endPoint', int(endPoint))
#roadSegment.prop("type", "RoadSegment")
roadSegment.gprop('location',(longitude,latitude))
roadSegment.prop('direction', roadShadow.get('direction'))
roadSegment.prop('edgeID', roadShadow.get('edgeID'))
#roadSegment.prop('trafficFlow', 0)
roadSegment.prop('status', "open")


road.rel(Rel.HAS_PART, roadSegment.id)
roadSegment.rel(Rel.IS_CONTAINED_IN, road.id)


# tl ENTITIES ALREADY EXIST IN THE CB, UPDATED BY THE IOT AGENT, THIS IS ONLY AN EXAMPLE
tlNumber = 1
tlID = 'TL{}'.format(tlNumber)
trafficLoop = Entity("Device", tlID, ctx=deviceContext)
trafficLoop.prop('trafficFlow', traffic_flow)
#properties that the cb can update on already existing entity
trafficLoop.rel(Rel.IS_CONTAINED_IN, roadSegment.id)
trafficLoop.prop('date', '01/02/2024')

# the CB has to trigger the update of the entity to which that flow is related and the trafficFlowobserved
tfoNumber = 1
tfoID = 'TFO{:03d}'.format(tfoNumber)
trafficFlowObs = Entity("TrafficFlowObserved", tfoID, ctx=transportationContext)
# time stamp should be added as "dateObserved"
trafficFlowObs.prop('laneDirection', roadShadow.get('direction'))
trafficFlowObs.rel('refRoadSegment', roadSegment.id)
trafficFlowObs.prop('intensity', traffic_flow).rel(Rel.OBSERVED_BY, trafficLoop.id, nested=True)


'''
# Step 1: Extract year, month, and day from the date string
day, month, year = map(int, date.split("/"))

# Step 2: Extract the end time from the time slot interval (24-hour format)
start_time, end_time = time_slot.split("-")  # Get both parts, e.g., "12:00" and "13:00"
start_hour_24 = int(start_time.split(":")[0])  # Extract the hour as an integer (12)
end_hour_24 = int(end_time.split(":")[0])  # Extract the hour as an integer (13 becomes 13)

# Step 3: Convert the 24-hour time to 12-hour format with AM/PM
# This handles converting 13:00 -> 1:00 PM, etc.
start_hour_12 = start_hour_24 % 12 or 12
start_meridiem = "PM" if start_hour_24 >= 12 else "AM"

end_hour_12 = end_hour_24 % 12 or 12
end_meridiem = "PM" if end_hour_24 >= 12 else "AM"

# Step 4: Generate a random delay in minutes (between 0 and 10)
random_delay = random.randint(0, 10)

# Step 5: Combine date and time
# Create a datetime object for the end time of the time slot
base_time = datetime(year, month, day, end_hour_24, 0)

# Add the random delay in minutes to the base time
final_time = base_time + timedelta(minutes=random_delay)

# Step 6: Format the final time as an ISO 8601 datetime string and include the AM/PM
d = final_time.strftime("%Y-%m-%dT%I:%M:%S") + "Z" #+ f" {meridiem}"
time_slot_12hr = f"{start_hour_12}:00{start_meridiem}-{end_hour_12}:00{end_meridiem}"
print(f"Time slot (12-hour format): {time_slot_12hr}")
# Output the result
print(f"Generated datetime: {d}")
'''
d = convertDate(date, time_slot)
print(d)


trafficFlowObs.tprop('DateTime',d)
roadSegment.prop('trafficFlow', traffic_flow).rel(Rel.OBSERVED_BY, trafficLoop.id, nested=True)
roadSegment.prop('refTrafficFlowObs', trafficFlowObs.id)
roadSegment.tprop('DateTime', d)
#road.pprint()
#roadSegment.pprint()
#trafficLoop.pprint()
#trafficFlowObs.pprint()


cb = Broker(pn=1026,pnt=None,host="localhost",fiwareservice="openiot")
cbConnection = cb.createConnection()
entitiesList = [road, roadSegment, trafficLoop, trafficFlowObs]

roadSegment1 = Entity("RoadSegment", "RS002", ctx=transportationContext)
roadSegment1.prop('edgeID', "a55")
roadSegment1.prop('trafficFlow', 1)
roadSegment1.prop('status', "open")

cbConnection.create(entitiesList)
cbConnection.create(roadSegment1)

#time.sleep(10)
generator = cbConnection.query_generator(type="https://smartdatamodels.org/dataModel.Transportation/RoadSegment")
e = next((e for e in generator if e["edgeID"].value == edgeID), None) #returning the first one matching the query
e.pprint()
#for e in g:
 #   e.pprint()


time_slot = "01:00-02:00"
traffic_flow = 26 # Example traffic flow count
date = "04/02/2024"
datanuova=convertDate(date=date, timeslot=time_slot)

e["trafficFlow"].value=traffic_flow
e.tprop("DateTime",datanuova)
response=cbConnection.update(e, overwrite=True)

flowObsid=e["refTrafficFlowObs"].value
eTFO = cbConnection.get(flowObsid)
eTFO.pprint()

#e.prop("trafficFlow", 10, observedat=d).rel(Rel.OBSERVED_BY, "urn:ngsi-ld:Device:TL1", nested=True)
#cbConnection.update(e)

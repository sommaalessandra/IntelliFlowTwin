import pandas as pd

from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.classes.Broker import Broker
from typing import List
from libraries.constants import shadowPath
import pandas as pd
from ngsildclient import CORE_CONTEXT




cb = Broker(pn=1026,pnt=None,host="localhost",fiwareservice="openiot")
cbConnection = cb.createConnection()

device_id = "TL26"
time_slot = "00:00-01:00"
traffic_flow = 10  # Example traffic flow count
coordinates : List[float] = [44.4937079783006, 11.3282993665462]
lane_direction = "E"  # Example lane direction


shadow_manager = DigitalShadowManager()
roadName, edgeID=shadow_manager.searchShadow(shadowType="road",timeSlot=time_slot,trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction, deviceID=device_id)
loopCode, loopLevel = shadow_manager.searchShadow(shadowType="trafficLoop",timeSlot=time_slot,trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction, deviceID=device_id)
print(roadName, edgeID)
print(loopCode, loopLevel)

#entities = client.query(type="AirQualityObserved", q="NO2>40")
# restart from HERE --> create an example road entity and query it

transportationContext= ["https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/4df15072b13da6c7bd7e86915df91fb28921aa7f/context.jsonld", CORE_CONTEXT]
deviceContext = ["https://raw.githubusercontent.com/smart-data-models/dataModel.Device/master/context.jsonld", CORE_CONTEXT]





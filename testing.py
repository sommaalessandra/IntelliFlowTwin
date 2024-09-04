import pandas as pd

from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.classes.Broker import Broker
from typing import List
from libraries.constants import shadowPath
import pandas as pd




cb = Broker(pn=1026,pnt=None,host="localhost",fiwareservice="openiot")
cbConnection = cb.createConnection()

device_id = "traffic_sensor_01"
time_slot = "00:00-01:00"
traffic_flow = 10  # Example traffic flow count
coordinates : List[float] = [44.4937079783006, 11.3282993665462]
lane_direction = "E"  # Example lane direction


shadow_manager = DigitalShadowManager()
roadName=shadow_manager.searchShadow(shadowType="road",timeSlot=time_slot,trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction)
print(roadName)

#entities = client.query(type="AirQualityObserved", q="NO2>40")
# restart from HERE --> create an example road entity and query it

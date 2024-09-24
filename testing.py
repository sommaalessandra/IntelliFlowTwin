import time
import pandas as pd
from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.classes.Broker import Broker
from typing import List
from libraries.constants import roadType
from ngsildclient import CORE_CONTEXT, Entity, Rel
from geojson import Point
#import json
import random
from datetime import datetime, timedelta
from libraries.general_utils import convertDate

cb = Broker(pn=1026,pnt=None,host="localhost",fiwareservice="openiot")
'''
device_id = "TL451"
time_slot = "00:00-01:00"
traffic_flow = 78 # Example traffic flow count
coordinates : List[float] = [44.5123626162894, 11.287461221671]
lane_direction = "NO"  # Example lane direction
date = "01/02/2024"

#tlNumber = 1
trafficLoop = Entity("Device", device_id)
trafficLoop.prop('trafficFlow', traffic_flow)
trafficLoop.prop('date', '01/02/2024')
cbConnection = cb.createConnection()
cbConnection.create(trafficLoop)

device_id = "TL61"
time_slot = "05:00-06:00"
traffic_flow = 59 # Example traffic flow count
coordinates : List[float] = [44.5012616462669, 11.3216426062022]
lane_direction = "SO"  # Example lane direction
date = "01/02/2024"

#tlNumber = 1
trafficLoop = Entity("Device", device_id)
trafficLoop.prop('trafficFlow', traffic_flow)
trafficLoop.prop('date', '01/02/2024')
cbConnection = cb.createConnection()
cbConnection.create(trafficLoop)
'''

device_id = "TL451"
time_slot = "00:00-01:00"
traffic_flow = 78 # Example traffic flow count
coordinates : List[float] = [44.5123626162894, 11.287461221671]
lane_direction = "NO"  # Example lane direction
date = "01/02/2024"

#tlNumber = 1
trafficLoop = Entity("Device", device_id)
trafficLoop.prop('trafficFlow', traffic_flow)
trafficLoop.prop('date', '01/02/2024')
cbConnection = cb.createConnection()
#cbConnection.create(trafficLoop)


cb.updateContext(deviceID=device_id, date=date, timeSlot=time_slot, trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction)
print(cb.getProgressiveNumber("Road"))

time.sleep(10)
device_id = "TL61"
time_slot = "05:00-06:00"
traffic_flow = 59 # Example traffic flow count
coordinates : List[float] = [44.5012616462669, 11.3216426062022]
lane_direction = "SO"  # Example lane direction
date = "01/02/2024"

#tlNumber = 1
trafficLoop = Entity("Device", device_id)
trafficLoop.prop('trafficFlow', traffic_flow)
trafficLoop.prop('date', '01/02/2024')
#cbConnection.create(trafficLoop)
cb.updateContext(deviceID=device_id, date=date, timeSlot=time_slot, trafficFlow=traffic_flow, coordinates=coordinates, laneDirection=lane_direction)
print(cb.getProgressiveNumber("Road"))
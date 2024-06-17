# ****************************************************
# Module Purpose: Simulates the behavior of the real system
#                 characterized by as traffic loops measurements. The traffic loop measures the number of passing cars
#                 through a specific road. Each traffic loop is paired with a sensor referring to the
#                 'TrafficFlowObserved' smart data model.
#                 Each device has a device_id and a device key (casually generated).
#
# Inputs:  agent_instance: the IoT Agent entity to which devices can
#          register themselves, register and send their measurements.
#
# Returns: The set of buses built as Physical System Connector class defined
#          as required by physical_adapter.py. These are returned as a result_queue
#          to allow multiprocessing and data sharing with other processes (main).
#****************************************************

from libraries.constants import *
from libraries.classes.physical_adapter import *
import threading

# the time slot column reports the number of cars that passed through a traffic loop sensor during that time frame
selectedTimeSlot = "00:00-01:00"
tlColumnsNames = ["index", selectedTimeSlot, "edge_id", "geopoint", "direzione"]

def setup_physicalsystem(agent_instance):
    traffic_loop = {}
    tfo = {}
    natural_number = 1
    key_length = 26

    [trafficdata, files] = reading_files(tlPath)
    # trafficdata = trafficdata[trafficdata['data'].str.contains('01/02/2024')]
    for i, file in enumerate(files):
        trafficdata[file].columns = tlColumnsNames

    ind = 0
    for i, file in enumerate(files):
        # the key is generated here because it is the same for all devices of the same type
        tfo_keys = generate_random_key(key_length)
        for index, rows in trafficdata[file].iterrows():
            if rows['edge_id'] not in traffic_loop.values():
                traffic_loop_name = "T{}".format(rows['edge_id'])
                traffic_loop[ind] = PhysicalSystemConnector(traffic_loop_name, file)
                tfo_id = "TFO{:03d}".format(natural_number)
                # tfo_keys = generate_random_key(key_length)
                tfo[i] = Sensor(tfo_id, devicekey=tfo_keys, name="TFO", sensortype="TrafficFlowObserved")
                traffic_loop[ind].add_sensors(tfo[i])
                traffic_loop[ind].save_connected_device(outputPath)
                ind +=1
                natural_number += 1

    # device and measurement registration
    device_entitytype = "Traffic Loop"
    for i in traffic_loop:
        for sensor in traffic_loop[i].sensors:
            agent_response = agent_instance.device_registration(sensor.device_partial_id, sensor.api_key, device_entitytype)
            if agent_response is not None:
                entitytype = "Device"
                timezone = "Europe/Rome"
                static_attribute = "urn:ngsi-ld:TrafficFlowObserved:{}".format(traffic_loop[i].name_identifier)
                if sensor.name == "TFO":
                    # if the devices has not been previously registered -> device measurement must be registered
                    measurement_type = "location"
                    measurement_response = agent_instance.measurement_registration(measurement_type, sensor.device_partial_id,
                                                                                   entitytype, timezone,
                                                                                   static_attribute)
                else:
                    raise TypeError("Only Traffic Flow Observed type is allowed")
    # result = bus
    return tfo, files
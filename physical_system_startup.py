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
from libraries.classes.iotagent_adapter import Agent
import threading

# the time slot column reports the number of cars that passed through a traffic loop sensor during that time frame
selectedTimeSlot = "00:00-01:00"
tlColumnsNames = ["index", "ID_loop", selectedTimeSlot, "edge_id", "geopoint", "direction"]

def setup_physicalsystem(agent_instance):
    trafficLoop = {}
    tfo = {}
    naturalNumber = 1
    keyLength = 26

    [trafficData, files] = reading_files(tlPath)
    # trafficdata = trafficdata[trafficdata['data'].str.contains('01/02/2024')]
    for i, file in enumerate(files):
        trafficData[file].columns = tlColumnsNames
    ind = 0
    for i, file in enumerate(files):
        # the key is generated here because it is the same for all devices of the same type
        tfo_keys = generate_random_key(keyLength)
        for index, rows in trafficData[file].iterrows():
            if rows['edge_id'] not in trafficLoop.values():
                traffic_loop_name = "T{}".format(naturalNumber)
                trafficLoop[ind] = PhysicalSystemConnector(naturalNumber, traffic_loop_name)
                # tfo_id = "TFO{:03d}".format(naturalNumber)
                # tfo_id = rows['edge_id']
                tfo_id = str(rows["ID_loop"])
                tfo[ind] = Sensor(tfo_id, devicekey=tfo_keys, name="TFO", sensortype="TrafficFlowObserved")
                tfo[ind].set_data_callback(agent_instance.retrievingData)
                trafficLoop[ind].add_sensors(tfo[ind])
                ### TODO: check to be added to avoid creating the same device inside the file
                trafficLoop[ind].save_connected_device(outputPath)
                ind +=1
                naturalNumber += 1

    # device and measurement registration
    deviceEntityType = "TrafficFlowObserved"
    for i in trafficLoop:
        for sensor in trafficLoop[i].sensors:
            # Service Group Registration
            agent_response = agent_instance.serviceGroupRegistration(sensor.device_partial_id, sensor.api_key, deviceEntityType)
            if agent_response is not None:
                entitytype = "TrafficFlowObserved"
                timezone = "Europe/Rome"
                static_attribute = "urn:ngsi-ld:TrafficLoop:{}".format(trafficLoop[i].name_identifier)
                if sensor.name == "TFO":
                    # if the devices has not been previously registered -> device measurement must be registered
                    measurement_type = "intensity"
                    measurement_response = agent_instance.measurementRegistration(measurement_type, sensor.device_partial_id,
                                                                                   entitytype, timezone,
                                                                                   static_attribute)
                else:
                    raise TypeError("Only Traffic Flow Observed type is allowed")
    # result = bus
    return trafficLoop, files

def start_physicalsystem(trafficLoop: dict[int, PhysicalSystemConnector]):
    """
    Starts the simulation of data transmission for each bus using threading.

    :param bus: A dictionary of buses initialized in the setup_physicalsystem function.
    """
    # STEP 3. DEVICE MEASUREMENTS TRANSMISSION SIMULATION
    [trafficData, files] = reading_files(tlPath)
    for i, file in enumerate(files):
        trafficData[file].columns = tlColumnsNames
    processingTlData(trafficData,trafficLoop)

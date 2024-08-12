# ****************************************************
# Module Purpose:
#   This library defines the Agent class, which is responsible for interacting with the FIWARE IoT Agent.
#   The Agent class manages the registration of devices and service groups, and handles the sending of
#   measurements to the IoT Agent.
#
#   - The Agent class includes attributes for agent identification, such as agent ID, port numbers,
#     FIWARE service, and service path.
#   - It provides methods for checking if a service group or device is already registered, registering
#     service groups, devices, and measurements, and sending data to the IoT Agent.
#   - The Agent class also handles the retrieval and transmission of sensor data, ensuring that measurements
#     are correctly formatted and sent to the specified endpoints.
#
# ****************************************************

import requests
from requests.structures import CaseInsensitiveDict
import json


class Agent:
    agentID: str
    brokerPortNumber: int
    southPortNumber: int
    northPortNumber: int
    fiwareService: str
    fiwareServicePath: str

    def __init__(self, aid: str, cb_port: int, south_port: int, northport: int, fw_service: str, fw_path: str):
        self.agentID = aid
        self.brokerPortNumber = cb_port
        self.southPortNumber = south_port
        self.northPortNumber = northport
        self.fiwareService = fw_service
        self.fiwareServicePath = fw_path

    def isServiceGroupRegistered(self, entity_type: str):
        # Check if the device is already registered
        url = "http://localhost:{}/iot/services".format(self.northPortNumber)
        header = CaseInsensitiveDict()
        header["fiware-service"] = self.fiwareService
        header["fiware-servicepath"] = self.fiwareServicePath
        response = requests.get(url, headers=header)
        # TODO: improve the type of check done to find the service group
        if entity_type in response.text:
            #print("Entity type found inside the body response")
            return True
        else:
            return False

    def isDeviceRegistered(self, device_id: str):
        # Check if the device is already registered
        url = "http://localhost:{}/iot/devices/{}".format(self.northPortNumber, device_id)
        header = CaseInsensitiveDict()
        header["fiware-service"] = self.fiwareService
        header["fiware-servicepath"] = self.fiwareServicePath
        response = requests.get(url, headers=header)
        # TODO: improve the type of check done to find the device
        if response.status_code == 200:
            #print("Device found")
            return True
        else:
            return False

    def getServiceGroupKey(self, entity_type):
        serviceKey = None

        # Check if the device is already registered
        url = "http://localhost:{}/iot/services".format(self.northPortNumber)
        header = CaseInsensitiveDict()
        header["fiware-service"] = self.fiwareService
        header["fiware-servicepath"] = self.fiwareServicePath
        response = requests.get(url, headers=header)
        # TODO: improve the type of check done to find the key
        if entity_type in response.text:
            #print("Entity type found inside the body response")
            services = response.json()["services"]
            for serv in services:
                if serv["entity_type"] == entity_type:
                    #print("Found it!")
                    serviceKey = serv["apikey"]
                    break
        return serviceKey

    def serviceGroupRegistration(self, api_key: str, entity_type: str):
        # register a Service Group in the IoT Agent (JSON version)
        if self.isServiceGroupRegistered(entity_type):
            print("Service is already registered. Skipping registration.")
            return True

        url_registration = "http://localhost:{}/iot/services".format(self.northPortNumber)
        # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = self.fiwareService
        header["fiware-servicepath"] = self.fiwareServicePath

        payload = {
            "services": [
                {
                    "apikey": api_key,
                    "cbroker": "http://orion:{}".format(self.brokerPortNumber),
                    "entity_type": entity_type,
                    "resource": "/iot/json"
                }
            ]
        }
        reg_response = requests.post(url_registration, headers=header, data=json.dumps(payload))
        return reg_response

    def measurementRegistration(self, measure_type: str, device_id: str, entity_type: str, timezone, controlled_asset: str):
        if self.isDeviceRegistered(device_id):
            print("Device is already registered. Skipping registration.")
            return True
        url_registration = "http://localhost:{}/iot/devices".format(self.northPortNumber)
        # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = self.fiwareService
        header["fiware-servicepath"] = self.fiwareServicePath

        payload = {}
        if measure_type == "trafficFlow":
            payload = {
                "devices": [
                    {
                        "device_id": device_id,
                        "entity_name": "urn:ngsi-ld:Device:{}".format(device_id),
                        "entity_type": entity_type,
                        "timezone": timezone,
                        "attributes": [
                            {"object_id": "trafficFlow", "name": "trafficFlow", "type": "Integer"},
                            {"object_id": "location", "name": "location", "type": "geo:point"},
                            {"object_id": "laneDirection", "name": "laneDirection", "type": "TextUnrestricted"}
                            #{"object_id": "timestamp", "name": "timestamp", "type": "DateTime"}
                        ],
                        "static_attributes": [
                            {"name": "deviceCategory", "type": "Text", "value": "Sensor"},
                            {"name": "controlledAsset", "type": "Relationship", "value": controlled_asset}
                        ]
                    }]}
        # print(payload)
        reg_response = requests.post(url_registration, headers=header, data=json.dumps(payload))
        return reg_response

    def retrievingData(self, *data, device_id, device_key):
        # TODO: befor even retrieving data we should check if there exist a device with
        #  that ID and if for that device the provided key is correct.

        flow = data[0][0]
        coordinates = data[0][1]
        direction = data[0][2]
        self.measurementSending(flow, coordinates, direction, measure_type="trafficFlow", device_key=device_key, device_id=device_id)


    def measurementSending(self, flow, coordinates, direction, measure_type, device_key, device_id):
        url_sending = "http://localhost:{}/iot/json?k={}&i={}".format(self.southPortNumber,
                                                                      device_key, device_id)
       # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = "openiot"
        header["fiware-servicepath"] = "/"

        payload = {}
        if measure_type == "trafficFlow":
            payload = {
                "trafficFlow": flow,
                "location": {
                    "type": "Point",
                    "coordinates": coordinates
                },
                "laneDirection": direction
            }
        sending_response = requests.post(url_sending, headers=header, data=json.dumps(payload))
        # if sending_response == 200:
            # TODO: according to the IoT Agent guidelines (see the activity diagram) after retrieving the iot device from the database the IoT agent has to map the values to entities attributes and trigger the context update

        return sending_response

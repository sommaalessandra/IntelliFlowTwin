import requests
from requests.structures import CaseInsensitiveDict
import json


class Agent:
    agent_id: str
    cb_port_number: int
    agent_southport_number: int
    agent_northport_number: int
    fiware_service: str
    fiware_service_path: str

    def __init__(self, aid, cb_port, south_port, northport, fw_service, fw_path):
        self.agent_id = aid
        self.cb_port_number = cb_port
        self.agent_southport_number = south_port
        self.agent_northport_number = northport
        self.fiware_service = fw_service
        self.fiware_service_path = fw_path

    def isServiceGroupRegistered(self, entity_type):
        # Check if the device is already registered
        url = "http://localhost:{}/iot/services".format(self.agent_northport_number)
        header = CaseInsensitiveDict()
        header["fiware-service"] = self.fiware_service
        header["fiware-servicepath"] = self.fiware_service_path
        response = requests.get(url, headers=header)
        # this check is too raw for me
        if entity_type in response.text:
            print("Entity type found inside the body response")
            return True
        else:
            return False
    def isDeviceRegistered(self, device_id):
        # Check if the device is already registered
        url = "http://localhost:{}/iot/devices/{}".format(self.agent_northport_number, device_id)
        header = CaseInsensitiveDict()
        header["fiware-service"] = self.fiware_service
        header["fiware-servicepath"] = self.fiware_service_path
        response = requests.get(url, headers=header)
        # this check is too raw for me
        if response.status_code == 200:
            print("Device found")
            return True
        else:
            return False

    def serviceGroupRegistration(self, device_id, api_key, entity_type):
        # register a Service Group in the IoT Agent (JSON version)
        if self.isServiceGroupRegistered(entity_type):
            print("Service is already registered. Skipping registration.")
            return True

        url_registration = "http://localhost:{}/iot/services".format(self.agent_northport_number)
        # print(url_registration)
        # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = self.fiware_service
        header["fiware-servicepath"] = self.fiware_service_path
        print(header)

        payload = {
            "services": [
                {
                    "apikey": api_key,
                    "cbroker": "http://orion:{}".format(self.cb_port_number),
                    "entity_type": entity_type,
                    "resource": "/iot/json"
                }
            ]
        }
        # print(payload)
        # payload_serialized = json.dumps(payload)
        reg_response = requests.post(url_registration, headers=header, data=json.dumps(payload))
        return reg_response

# TODO: from here on, functions to be changed
    def measurementRegistration(self, measure_type, device_id, entity_type, timezone, controlled_asset):
        if self.isDeviceRegistered(device_id):
            print("Device is already registered. Skipping registration.")
            return True
        url_registration = "http://localhost:{}/iot/devices".format(self.agent_northport_number)
        # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = self.fiware_service
        header["fiware-servicepath"] = self.fiware_service_path

        payload = {}
        # TODO: check if this type is compliant to the one of the FIWARE SDM
        if measure_type == "trafficFlow":
            payload = {
                "devices": [
                    {
                        "device_id": device_id,
                        "entity_name": "urn:ngsi-ld:{}:{}".format(entity_type, device_id),
                        "entity_type": entity_type,
                        "timezone": timezone,
                        "attributes": [
                            {"object_id": "location", "name": "location", "type": "geo:point"},
                            {"object_id": "trafficFlow", "name": "trafficFlow", "type": "Integer"},
                            {"object_id": "timestamp", "name": "timestamp", "type": "DateTime"}
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
        # --------- to be ADDED: CHECK IF DEVICE ID AND DEVICE KEY EXISTS OTHERWISE RAISE EXCEPTION

        flow = data[0][0]
        coordinates = data[0][1]
        direction = data[0][2]
        self.measurementSending(flow, coordinates, direction, measure_type="trafficFlow", device_key=device_key, device_id=device_id)


    def measurementSending(self, flow, coordinates, direction, measure_type, device_key, device_id):
        url_sending = "http://localhost:{}/iot/json?k={}&i={}".format(self.agent_southport_number,
                                                                      device_key, device_id)
       # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = "openiot"
        header["fiware-servicepath"] = "/"

        payload = {}
        if measure_type == "trafficFlow":
            payload = {
                "trafficFlow": int(flow),
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

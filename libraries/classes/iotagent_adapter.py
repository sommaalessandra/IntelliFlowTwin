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

    def is_device_registered(self, device_id):
        # Check if the device is already registered
        url = "http://localhost:{}/iot/devices/{}".format(self.agent_northport_number, device_id)
        header = CaseInsensitiveDict()
        header["fiware-service"] = self.fiware_service
        header["fiware-servicepath"] = self.fiware_service_path
        response = requests.get(url, headers=header)
        return response.status_code == 200

    def device_registration(self, device_id, api_key, entity_type):
        # register a device in the IoT Agent (JSON version)
        if self.is_device_registered(device_id):
            print("Device is already registered. Skipping registration.")
            return

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
    def measurement_registration(self, measure_type, device_id, entity_type, timezone, controlled_asset):
        url_registration = "http://localhost:{}/iot/devices".format(self.agent_northport_number)
        # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = self.fiware_service
        header["fiware-servicepath"] = self.fiware_service_path

        payload = {}
        # TODO: check if this type is compliant to the one of the FIWARE SDM
        if measure_type == "location":
            payload = {
                "devices": [
                    {
                        "device_id": device_id,
                        "entity_name": "urn:ngsi-ld:{}:{}".format(entity_type, device_id),
                        "entity_type": entity_type,
                        "timezone": timezone,
                        "attributes": [
                            {"object_id": "location", "name": "location", "type": "geo:point"},
                            {"object_id": "timestamp", "name": "timestamp", "type": "DateTime"},
                            {"object_id": "arrivaltime", "name": "arrivaltime", "type": "DateTime"}
                        ],
                        "static_attributes": [
                            {"name": "deviceCategory", "type": "Text", "value": "Sensor"},
                            {"name": "controlledAsset", "type": "Relationship", "value": controlled_asset}
                        ]
                    }
                ]
            }
        # left here, could remove it later
        elif measure_type == "occupancy":
            payload = {
                "devices": [
                    {
                        "device_id": device_id,
                        "entity_name": "urn:ngsi-ld:{}:{}".format(entity_type, device_id),
                        "entity_type": entity_type,
                        "timezone": timezone,
                        "attributes": [
                            {"object_id": "occupancy", "name": "occupancy", "type": "Integer"},
                            {"object_id": "timestamp", "name": "timestamp", "type": "DateTime"},
                            {"object_id": "arrivaltime", "name": "arrivaltime", "type": "DateTime"}
                        ],
                        "static_attributes": [
                            {"name": "deviceCategory", "type": "Text", "value": "Sensor"},
                            {"name": "controlledAsset", "type": "Relationship", "value": controlled_asset}
                        ]
                    }]}

        # print(payload)
        reg_response = requests.post(url_registration, headers=header, data=json.dumps(payload))
        return reg_response

    def retrieving_data(self, *data, device_id, device_key):
        # --------- to be ADDED: CHECK IF DEVICE ID AND DEVICE KEY EXISTS OTHERWISE RAISE EXCEPTION
        if "GPS" in str(device_id):
            # print("Processing location data...")
            coordinates = data[0][0]
            timestamp = data[0][1]
            arrivaltime = data[0][2]
            self.sending_location(coordinates, timestamp, arrivaltime, device_id=device_id, device_key=device_key)
        elif "APC" in str(device_id):
            # print("Processing occupancy data...")
            occupancy = data[0][0]
            timestamp = data[0][1]
            arrivaltime = data[0][2]
            self.sending_occupancy(occupancy, timestamp, arrivaltime, device_id=device_id, device_key=device_key)
        elif isinstance(device_id,int):
            flow = data[0][0]
            coordinates = data[0][1]
            direction = data[0][2]
            self.sending_flow(flow, coordinates, direction, device_id=device_id, device_key=device_key)
        else:
            raise TypeError("Unkwown device type")

    def sending_location(self, coordinates, timestamp, arrivaltime, device_id, device_key):
        # coordinates = ast.literal_eval(coordinates)
        self.measurement_sending(coordinates, timestamp, arrivaltime, measure_type="location",
                                 device_key=device_key, device_id=device_id)

    def sending_occupancy(self, occupancy, timestamp, arrivaltime, device_id, device_key):
        self.measurement_sending(occupancy, timestamp, arrivaltime, measure_type="occupancy",
                                 device_key=device_key, device_id=device_id)

    def sending_flow(self, flow, coordinates, direction, device_id, device_key):
        self.measurement_sending(flow, coordinates, direction, measure_type="intensity",
                                 device_key=device_key, device_id=device_id)

    def measurement_sending(self, flow, coordinates, direction, measure_type, device_key, device_id):
        url_sending = "http://localhost:{}/iot/json?k={}&i={}".format(self.agent_southport_number,
                                                                      device_key, device_id)
        # print(url_sending)
        # building packet header and payload
        header = CaseInsensitiveDict()
        header["Content-Type"] = "application/json"
        header["fiware-service"] = "openiot"
        header["fiware-servicepath"] = "/"

        payload = {}
        if measure_type == "intensity":
            payload = {
                "intensity": int(flow),
                "location": {
                    "type": "Point",
                    "coordinates": coordinates
                },
                "laneDirection": direction
            }
        # print(payload)
        sending_response = requests.post(url_sending, headers=header, data=json.dumps(payload))
        # if sending_response == 200:
            # TODO: according to the IoT Agent guidelines (see the activity diagram) after retrieving the iot device from the database the IoT agent has to map the values to entities attributes and trigger the context update

        return sending_response

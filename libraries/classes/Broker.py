from ngsildclient import Client
from typing import Optional, List
from libraries.classes.DigitalShadowManager import DigitalShadowManager

class Broker:
    portNumber: int
    portTemporal: Optional[int]
    fiwareService: str
    hostname: str

    def __init__(self, pn: int, pnt: Optional[int], host: str, fiwareservice: str):
        self.portNumber = pn
        self.portTemporal = pnt
        self.hostname = host
        self.fiwareService = fiwareservice

    def createConnection(self) -> Client:
        try:
            if self.portTemporal is None:
                cb = Client(hostname=self.hostname, port=self.portNumber, tenant=self.fiwareService, overwrite=True)
            else:
                cb = Client(hostname=self.hostname, port=self.portNumber, port_temporal=self.portTemporal,
                            tenant=self.fiwareService, overwrite=True)
            return cb
        except Exception as e:
            raise ConnectionError(f"Impossible to connect: {str(e)}")


    def updateContext(self, deviceid, timeSlot: str, trafficFlow: int, coordinates: List[float], laneDirection: str):
        shadowManager = DigitalShadowManager()
        roadName = shadowManager.searchShadow(timeSlot=timeSlot, trafficFlow=trafficFlow, coordinates=coordinates, laneDirection=laneDirection)
        # search entity
        self.createConnection()


        return True






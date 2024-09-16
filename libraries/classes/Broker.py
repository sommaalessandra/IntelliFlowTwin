from ngsildclient import Client, Entity
from typing import Optional, List
from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.constants import roadSegmentType

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


    def updateContext(self, deviceID:str, date: str, timeSlot: str, trafficFlow: int, coordinates: List[float], laneDirection: str):
        shadowManager = DigitalShadowManager()
        roadName, edgeID = shadowManager.searchShadow(shadowType="road", timeSlot=timeSlot, trafficFlow=trafficFlow,
                                                      coordinates=coordinates, laneDirection=laneDirection, deviceID=deviceID)

        # search entity
        cbConnection=self.createConnection()
        e = self.searchRoadSegmentEntity(cbConnection=cbConnection,edgeID=edgeID)
        if e is not None:
            return True #update della prop
        else:
            return True # creo l'entity --> devo avere a disposizione anche tutte le entity ad essa collegate, oppure fare funzioni per update
        #delle singole prop

    def searchRoadSegmentEntity(self, cbConnection: Client, edgeID: str) -> Entity:
        generator = cbConnection.query_generator(type=roadSegmentType)
        e: Entity | None = next((e for e in generator if e["edgeID"].value == edgeID), None)
        return e

    def updateFlow(self):
        return True



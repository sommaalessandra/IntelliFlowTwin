from ngsildclient import Client, Entity
from typing import Optional, List
from libraries.classes.DigitalShadowManager import DigitalShadowManager
from libraries.constants import transportationCTX, roadSegmentType
from libraries.general_utils import convertDate

class Broker:
    portNumber: int
    portTemporal: Optional[int]
    fiwareService: str
    hostname: str
    cityContext: bool

    def __init__(self, pn: int, pnt: Optional[int], host: str, fiwareservice: str):
        self.portNumber = pn
        self.portTemporal = pnt
        self.hostname = host
        self.fiwareService = fiwareservice

    def createConnection(self) -> Client:
        """
        Establish a connection to the Context Broker.
        """
        try:
            if self.portTemporal is None:
                cb = Client(hostname=self.hostname, port=self.portNumber, tenant=self.fiwareService, overwrite=True)
            else:
                cb = Client(hostname=self.hostname, port=self.portNumber, port_temporal=self.portTemporal,
                            tenant=self.fiwareService, overwrite=True)
            return cb
        except Exception as e:
            raise ConnectionError(f"Impossible to connect: {str(e)}")

    def updateContext(self, deviceID:str, date: str, timeSlot: str, trafficFlow: int, coordinates: List[float], laneDirection: str) -> bool:
        """
        Update the existing Context entities according to data received from the Physical World through the IoT Agent.
        If the Context is not already created, it will be set up the static context with the modeled entities.

        """
        try:
            shadowManager = DigitalShadowManager()
            roadShadow = shadowManager.searchShadow(shadowType="road", timeSlot=timeSlot, trafficFlow=trafficFlow,
                                                          coordinates=coordinates, laneDirection=laneDirection, deviceID=deviceID)

            roadName = roadShadow.name
            edgeID = roadShadow.get('edgeID')
            startPoint = roadShadow.get('startPoint')
            endPoint = roadShadow.get('endPoint')

            cbConnection=self.createConnection()
            if not self.cityContext:
                deviceURN = "urn:ngsi-ld:Device:{}".format(deviceID)
                if cbConnection.get(deviceURN) is not None:
                    completeDate = convertDate(date=date, timeslot=timeSlot)
                    return self.createContext(cbConnection=cbConnection, deviceURN=deviceURN, date=completeDate, trafficFlow=trafficFlow,
                                              coordinates=coordinates, laneDirection=laneDirection, roadName=roadName,
                                              edgeID=edgeID, startPoint=startPoint, endPoint=endPoint)
            # Search for RoadSegment and TrafficFlowObserved entities to update the traffic flow related attributes.
            entityRoadSegment = self.searchEntity(cbConnection=cbConnection, edgeID=edgeID, eType="RoadSegment")
            if entityRoadSegment is not None:
                completeTimestamp = convertDate(date=date, timeslot=timeSlot)
                if self.updateFlow(cbConnection=cbConnection, newFlow=trafficFlow, date=completeTimestamp,
                                   cEntity=entityRoadSegment, eType="RoadSegment"):
                    trafficFlowObsID = entityRoadSegment['refTrafficFlowObserved'].value
                    trafficFlowObs = cbConnection.get(trafficFlowObsID)
                    if trafficFlowObs is not None:
                        return self.updateFlow(cbConnection=cbConnection, newFlow=trafficFlow,
                                               date=completeTimestamp, cEntity=trafficFlowObs,
                                               eType="TrafficFlowObserved")
                return False
            return False

        except Exception as e:
            print(f"Error during context update: {str(e)}")
            return False

    def createContext(self, cbConnection: Client, deviceURN: str, date: str, trafficFlow: int, coordinates: List[float],
                      laneDirection: str, roadName: str, edgeID: str, startPoint: str, endPoint: str) -> bool:
        # create entity road
        # create entity road segment
        # update rel between road and road segment
        # create entity traffic flow obs
        # update relation between road segment and traffic flow obs
        # set the city context to true to remember that the static context has been created

        self.cityContext = True
        return self.cityContext


    def createRoadEntity(self):

        #roadID = 'R{:03d}'.format(roadNumber)
        #road = Entity("Road", roadID, ctx=transportationContext)
        #road.prop('alternateName', roadName)
        return True

    def createRoadSegmentEntity(self):
        return True

    def createTrafficFlowObsEntity(self):
        return True




    def searchEntity(self, cbConnection: Client, edgeID: str, eType: str) -> Entity:
        if eType == "RoadSegment":
            generator = cbConnection.query_generator(type=roadSegmentType)
            e: Entity | None = next((e for e in generator if e["edgeID"].value == edgeID), None)
            return e

    def updateFlow(self, cbConnection: Client, newFlow: int, date: str, cEntity: Entity, eType: str) -> bool:
        if eType == "RoadSegment":
            cEntity["trafficFlow"].value = newFlow
            cEntity.tprop("DateTime",date)
            response = cbConnection.update(cEntity, overwrite=True)
            return response
        elif eType=="TrafficFlowObserved":
            cEntity["intensity"].value = newFlow
            cEntity.tprop('DateTime',date)
            response = cbConnection.update(cEntity, overwrite=True)
            return response
        else:
            return False



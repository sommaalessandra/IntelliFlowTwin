import typing
from libraries.constants import shadowPath, shadowFilePath
import pandas as pd
import os


class Shadow:
    name: str

    def __init__(self, name: str, **attributes):
        self.name = name
        for key, value in attributes.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Shadow(name={self.name}, attributes={self.__dict__})"

    def get(self, attribute: str) -> typing.Any:
        # get an attribute
        return getattr(self, attribute, None)

    def set(self, attribute: str, value: typing.Any) -> None:
        # set an attribute to value
        setattr(self, attribute, value)

    def getAllAttributes(self) -> typing.Dict[str, typing.Any]:
        # retrieve all attributes
        return self.__dict__


class DataProcessor:

    def __init__(self, datapath):
        self.df = pd.read_csv(datapath)

    def searchRoad(self, coordinates, direction: str) -> typing.Tuple[str, str]:
        if self.df.empty:
            raise ValueError("The DataFrame is empty or not loaded correctly.")
        # The +/- 0.001 buffer can be added to account for small variations in data (e.g., when we will receive real gps
        # data).
        coordinatestr = f"{coordinates[0]}, {coordinates[1]}"

        # Filter the DataFrame based on 'geopoint' and 'direzione'
        matchingRow = self.df[
            (self.df['geopoint'] == coordinatestr) &
            (self.df['direzione'].str.lower() == direction.lower())
            ]

        if matchingRow.empty:
            raise ValueError(
                f"No matching rows found for the given coordinates {coordinates} and direction {direction}.")
        if len(matchingRow) > 1:
            raise ValueError("Multiple matching rows found; expected a single match.")
        roadName = matchingRow.iloc[0]['Nome via']
        edgeID = matchingRow.iloc[0]['edge_id']
        return roadName, edgeID

    def searchTrafficLoop(self, deviceID: str, coordinates, direction: str) -> typing.Tuple[str, int] :
        if self.df.empty:
            raise ValueError("The DataFrame is empty or not loaded correctly.")

        coordinatestr = f"{coordinates[0]}, {coordinates[1]}"
        loopID = deviceID.split('TL')[-1]

        self.df['geopoint'] = self.df['geopoint'].astype(str).str.strip()
        self.df['ID_univoco_stazione_spira'] = self.df['ID_univoco_stazione_spira'].astype(str).str.strip()
        self.df['direzione'] = self.df['direzione'].str.strip().str.lower()

        # Filter based on coordinates, unique station ID, and direction
        matchingRow = self.df[
            (self.df['geopoint'] == coordinatestr) &
            (self.df['ID_univoco_stazione_spira'] == loopID) &
            (self.df['direzione'] == direction.lower())
            ]

        if matchingRow.empty:
            raise ValueError(
                f"No matching rows found for the given coordinates {coordinates}, direction {direction} and unique TL ID {loopID}.")
        if len(matchingRow) > 1:
            raise ValueError("Multiple matching rows found; expected a single match.")
        loopCode = str(matchingRow.iloc[0]['codice_spira'])
        loopLevel = int(matchingRow.iloc[0]['livello_spira'])
        return loopCode, loopLevel



class DigitalShadowManager:

    def __init__(self):
        self.shadowsByTypes: typing.Dict[str, typing.List[Shadow]] = {}
        self.dataProcessor = DataProcessor(shadowFilePath)

    def addShadow(self, shadowType: str, timeSlot: str, trafficFlow: int, coordinates: typing.List[float],direction: str, deviceID: str) -> Shadow:
        try:
            if shadowType == "road":
                roadName, edgeID = self.dataProcessor.searchRoad(coordinates=coordinates, direction=direction)
                shadowAttributes = {
                    "timeSlot": timeSlot,
                    "trafficFlow": trafficFlow,
                    "coordinates": coordinates,
                    "direction": direction,
                    "edgeID": edgeID
                }

                newShadow = Shadow(name=roadName, **shadowAttributes)
                # adding the shadow to the shadow list w.r.t the appropriate type
                if shadowType not in self.shadowsByTypes:
                    self.shadowsByTypes[shadowType] = []
                self.shadowsByTypes[shadowType].append(newShadow)
                self.saveShadowToCSV(shadowType=shadowType, shadow=newShadow)
                return newShadow
            elif shadowType == "trafficLoop":
                loopCode, loopLevel = self.dataProcessor.searchTrafficLoop(coordinates=coordinates,direction=direction,deviceID=deviceID)
                shadowAttributes = {
                    "deviceID": deviceID,
                    "coordinates": coordinates,
                    "timeSlot": timeSlot,
                    "trafficFlow": trafficFlow,
                    "loopCode": loopCode,
                    "loopLevel": loopLevel
                }
                newShadow = Shadow(name=deviceID, **shadowAttributes)
                if shadowType not in self.shadowsByTypes:
                    self.shadowsByTypes[shadowType] = []
                self.shadowsByTypes[shadowType].append(newShadow)
                self.saveShadowToCSV(shadowType=shadowType, shadow=newShadow)
                return newShadow

        except ValueError as e:
            print(f"Error occurred: {e}")
            raise RuntimeError(f"Failed to create shadow: {e}")

    def searchShadow(self, shadowType: str, timeSlot: str, trafficFlow: int, coordinates: typing.List[float], laneDirection: str, deviceID: str) -> typing.Tuple[str,str]:
        if shadowType in self.shadowsByTypes and shadowType == "road":
            for shadow in self.shadowsByTypes[shadowType]:
                if (shadow.get("coordinates") == coordinates and
                        shadow.get("direction") == laneDirection and
                        shadow.get("trafficFlow") == trafficFlow):
                    return shadow.name, shadow.get("edgeID") # returns the roadName
        elif shadowType in self.shadowsByTypes and shadowType == "trafficLoop":
            for shadow in self.shadowsByTypes[shadowType]:
                if (shadow.get("coordinates") == coordinates and
                        shadow.name == deviceID and
                        shadow.get("trafficFlow") == trafficFlow):
                    return shadow.get("loopCode"), shadow.get("loopLevel")

        # if no matching shadow is found, it creates a new one
        try:
            if shadowType == "road":
                newShadow = self.addShadow(shadowType, timeSlot=timeSlot, trafficFlow=trafficFlow,coordinates=coordinates, direction=laneDirection, deviceID=deviceID)
                return newShadow.name, newShadow.get("edgeID")
            elif shadowType == "trafficLoop":
                newShadow = self.addShadow(shadowType, timeSlot=timeSlot, trafficFlow=trafficFlow,coordinates=coordinates, direction=laneDirection, deviceID=deviceID)
                return newShadow.get("loopCode"), newShadow.get("loopLevel")

        except RuntimeError as e:
            print(f"Error in searchShadow: {e}")
            raise ValueError("Unable to create or find the shadow.")


    def saveShadowToCSV(self, shadowType: str, shadow: Shadow):
        """
        Save shadow data to the CSV file inside the folder digital_shadows/shadowType.
        """
        directoryPath = os.path.join(shadowPath, shadowType)
        os.makedirs(directoryPath, exist_ok=True)
        fileName = shadow.name.replace(" ", "_") + ".csv"
        filePath = os.path.join(directoryPath, fileName)


        shadowAttributes = shadow.getAllAttributes()
        coordinates = shadowAttributes.get("coordinates", [None, None])

        # Add latitude and longitude columns
        shadowAttributes["latitude"] = coordinates[0]
        shadowAttributes["longitude"] = coordinates[1]

        # Create a DataFrame directly from the shadow attributes
        shadowData = pd.DataFrame([shadowAttributes])

        if os.path.exists(filePath):
            shadowData.to_csv(filePath, mode='a', header=False, index=False)
        else:
            shadowData.to_csv(filePath, mode='w', header=True, index=False)

import typing
from libraries.constants import shadowPath
import pandas as pd


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

    def get_all_attributes(self) -> typing.Dict[str, typing.Any]:
        # retrieve all attributes
        return self.__dict__


class DataProcessor:

    def __init__(self, datapath):
        self.df = pd.read_csv(datapath)

    def searchRoad(self, coordinates: typing.List[float], direction: str) -> str:
        # The +/- 0.001 buffer can be added to account for small variations in data (e.g., when we will receive real gps
        # data).
        matching_row = self.df[
            (self.df['latitudine'] == coordinates[0]) & (self.df['longitudine'] == coordinates[1]) &
            (self.df['direzione'] == direction)]
        if matching_row.empty:
            raise ValueError(
                f"No matching rows found for the given coordinates {coordinates} and direction {direction}.")
        if len(matching_row) > 1:
            raise ValueError("Multiple matching rows found; expected a single match.")
        roadName = matching_row.iloc[0]['Nome via']
        return roadName


class DigitalShadowManager:

    def __init__(self):
        self.shadowsByTypes: typing.Dict[str, typing.List[Shadow]] = {}
        self.dataProcessor = DataProcessor(shadowPath)

    def addShadow(self, shadowType: str, timeSlot: str, trafficFlow: int, coordinates: typing.List[float],
                  direction: str) -> Shadow:
        try:
            roadName = self.dataProcessor.searchRoad(coordinates=coordinates, direction=direction)
            shadow_attributes = {
                "timeSlot": timeSlot,
                "trafficFlow": trafficFlow,
                "coordinates": coordinates,
                "direction": direction
            }

            newShadow = Shadow(name=roadName, **shadow_attributes)
            # adding the shadow to the shadow list w.r.t the appropriate type
            if shadowType not in self.shadowsByTypes:
                self.shadowsByTypes[shadowType] = []
            self.shadowsByTypes[shadowType].append(newShadow)
            return newShadow

        except ValueError as e:
            print(f"Error occurred: {e}")
            raise RuntimeError(f"Failed to create shadow: {e}")

    def searchShadow(self, shadowType: str, timeSlot: str, trafficFlow: int, coordinates: typing.List[float],
                     laneDirection: str) -> str:
        if shadowType in self.shadowsByTypes:
            for shadow in self.shadowsByTypes[shadowType]:
                if (shadow.get("coordinates") == coordinates and
                        shadow.get("direction") == laneDirection and
                        shadow.get("trafficFlow") == trafficFlow):
                    return shadow.name  # returns the roadName

        # if no matching shadow is found, it creates a new one
        try:
            roadShadow = self.addShadow(shadowType, timeSlot=timeSlot, trafficFlow=trafficFlow, coordinates=coordinates,
                                        direction=laneDirection)
            return roadShadow.name
        except RuntimeError as e:
            print(f"Error in searchShadow: {e}")
            raise ValueError("Unable to create or find the road shadow.")

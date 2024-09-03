from typing import Dict, List
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

class DataProcessor:

    def __init__(self, datapath):
        self.df = pd.read_csv(datapath)

    def processData(self, coordinates: List[float], direction: str) -> str:
        # The +/- 0.001 buffer can be added to account for small variations in data (when we will receive real gps
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
        self.shadowsByTypes: Dict[str, List[Shadow]] = {}
        self.dataProcessor = DataProcessor(shadowPath)

    def addShadow(self, shadowType: str, timeSlot: str, trafficFlow: int, coordinates: List[float], direction: str):
        try:
            roadName = self.dataProcessor.processData(coordinates=coordinates, direction=direction)
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
            return True

        except ValueError as e:
            print(f"Error: {e}")
            return False





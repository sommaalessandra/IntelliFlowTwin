from typing import Dict, List
from libraries.constants import tlPath
import pandas as pd


class Shadow:
    name: str

    def __init__(self, name: str, sdata):
        self.name = name
        self.data = sdata



class DataProcessor:

    def __init__(self, datapath):
        self.df = pd.read_csv(datapath)

    def processData(self, timeSlot: str, trafficFlow: int, coordinates: List[float], direction: str) -> str:
        row = self.df.iloc
        roadName = self.df
        return roadName



class DigitalShadowManager:
    def __init__(self):
        self.shadowsByTypes: Dict[str, List[Shadow]] = {}
        self.dataProcessor = DataProcessor(tlPath)


    def addshadow(self, shadowtype: str, timeSlot: str, trafficFlow: int, coordinates: List[float], direction: str):
        roadName=self.dataProcessor.processData()
        newShadow = Shadow(name=roadName)
        newShadow # add attributes timeSlot: str, trafficFlow: int, coordinates: List, direction: str
        if shadowType not in self.shadowsByTypes:
            self.shadowsByTypes[shadowtype] = []

        self.shadowsByTypes[shadowtype].append()


        return True





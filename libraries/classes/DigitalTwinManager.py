from libraries.classes.SumoSimulator import Simulator
from libraries.classes.Planner import Planner
from libraries.classes.DataManager import DataManager
from typing import Optional
import pytz
from datetime import datetime


class DigitalTwinManager:
    """
    The DigitalTwinManager class orchestrates the interaction between historical traffic data, SUMO simulations,
    and traffic planning to create a digital twin environment. This class is essential for running simulations
    based on real-world data to support traffic flow analysis.

    Attributes:
       sumoSimulator (Simulator): An instance of the Simulator class, which runs the SUMO simulation.
       planner (Planner): An instance of the Planner class, responsible for scenario planning.
       dtDataManager (DataManager): An instance of the DataManager class, which handles data retrieval and storage.

    Methods:
       - __init__: Initializes the DigitalTwinManager by setting up the DataManager, Simulator, and Planner instances.
       - simulateBasicScenarioForOneHourSlot: Simulates a basic scenario for a one-hour time slot using historical data.
   """

    sumoSimulator: Simulator
    planner: Planner
    dtDataManager: DataManager

    def __init__(self, dataManager: DataManager, sumoConfigurationPath: str, sumoLogFile: str):
        """
        Initializes the DigitalTwinManager by creating instances of the DataManager, SUMO simulator, and Planner.

        :param dataManager: Optional name for the DataManager (default is "DataManager").
        :param sumoConfigurationPath: Path to the SUMO configuration file.
        :param sumoLogFile: Path to the log file for SUMO.
        """
        # TODO: manage the possibility to get as input directly the simulator and the planner instances.
        self.dtDataManager = dataManager
        self.sumoSimulator = Simulator(configurationPath=sumoConfigurationPath, logFile=sumoLogFile)
        self.planner = Planner(simulator=self.sumoSimulator)

    def simulateBasicScenarioForOneHourSlot(self, timeslot: str, date: str, entityType: str, totalVehicles: int,
                                            minLoops: int, congestioned: bool, activeGui: bool=False, timecolumn: Optional[str] = "timeslot"):
        """
        Simulates a basic traffic scenario for a one-hour time slot, retrieving historical data and using it to
        define the simulation parameters.

        :param timeslot: The time slot for which historical traffic data is retrieved (e.g., "00:00-01:00").
        :param date: The date on which the traffic data is based (e.g., "2024-02-01").
        :param entityType: The type of entity being simulated (e.g., "roadsegment" or "device").
        :param totalVehicles: The total number of vehicles to include in the simulation.
        :param minLoops: The minimum number of simulation loops to perform.
        :param congestioned: A boolean flag to indicate if the simulation should include congestion.
        :param activeGui: Whether to activate the SUMO graphical user interface (GUI) during the simulation.
        :param timecolumn: The name of the time column in the database used to retrieve historical data (default is "timeslot").

        :return: A string representing the folder where the scenario is stored.
        """
        if entityType.lower() in ["road segment", "roadsegment"]:
            timescaleManager = self.dtDataManager.getDBManagerByType("TimescaleDBManager")
            df = timescaleManager.retrieveHistoricalDataForTimeslot(timeslot=timeslot, date=date, entityType=entityType, timecolumn=timecolumn)
            scenarioFolder = self.planner.planBasicScenarioForOneHourSlot(df, entityType=entityType, totalVehicles=totalVehicles,
                                                                         minLoops=minLoops, congestioned=False, activeGui=activeGui)
            return scenarioFolder





from libraries.classes import Agent
import os
import sys
import psycopg2
from libraries import constants, general_utils
from libraries.classes import Simulator
import xml.etree.ElementTree as ET
import pandas as pd
import subprocess
import datetime
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename


class ScenarioGenerator:
    """
    The ScenarioGenerator class handles scenarios as traffic routes, allowing them to be created and configured.
    It also sets up these within the simulator.
    """
    sumoConfiguration: str
    sim: Simulator

    def __init__(self, sumocfg: str, sim: Simulator):
        self.sumoConfiguration = sumocfg
        self.sim = sim

    # Function to generate routes starting from an edgefile with counting vehicles
    def generateRoutes(self, edgefile: str, totalVehicles: int, minLoops = 1, congestioned = False):
        """
        Starting from an edgefile containing the traffic counts for the network edges, generate a new route file made
        for SUMO simulation. The :param totalVehicles sets the total number of generated vehicles and
        :param minLoops sets the minimum number of counting location covered by each vehicle route.
        Using :param congestioned, the routefile generated is configured to generate some traffic congestion during
        the simulation.
        """
        if edgefile is None:
            print("No edgefile was given")
            return None
        if totalVehicles is None:
            print("The total number of vehicles was not defined")
            return
        if os.path.exists(constants.sumoToolsPath):
            date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            if congestioned:
                newpath = constants.simulationPath + date + "_congestioned/"
            else:
                newpath = constants.simulationPath + date + "_basic/"
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            script1 = constants.sumoToolsPath + "/randomTrips.py"
            arg1 = constants.sumoToolsPath + "\\joined_lanes.net.xml"
            subprocess.run(['python', script1, "-n", arg1, "-r", newpath +
                            "sampleRoutes.rou.xml", "--fringe-factor", "10", "--random", "--min-distance",
                            "100", "--random-factor", "200"])


            script2 = constants.sumoToolsPath + "/routeSampler.py"
            if congestioned:
                #TODO: here some actions has to be taken in order to generate a congestioned scenario. Note that using
                # the totalVehicles parameters and the minLoops can generate congestioned traffic even if this parameter
                # is not set.
                subprocess.run([sys.executable,  script2, "-r", newpath + "sampleRoutes.rou.xml",
                            "--edgedata-files", edgefile, "-o", newpath +
                            "generatedRoutes.rou.xml", "--total-count", str(totalVehicles), "--optimize",
                            "full", "--min-count", str(minLoops)])
            else:
                subprocess.run([sys.executable,  script2, "-r", newpath + "sampleRoutes.rou.xml",
                            "--edgedata-files", edgefile, "-o", newpath +
                            "generatedRoutes.rou.xml", "--total-count", str(totalVehicles), "--optimize",
                            "full", "--min-count", str(minLoops)])
            print("Routes Generated")
            # self.sim.changeRoutePath(newpath + "generatedRoutes.rou.xml")

            relativeRouteFile = newpath + "generatedRoutes.rou.xml"
            routeFile = os.path.abspath(relativeRouteFile)
            return routeFile
            # self.setScenario()


    def setScenario(self, routeFilePath = None,manual = False):

        if not manual and (routeFilePath is not None):
            self.sim.changeRoutePath(routeFilePath)
        elif manual:
            Tk().withdraw()
            routeFilePath = askopenfilename(title= "Select a Route File", filetypes = (("route files","*.rou.xml"),("xml files","*.xml")))
            if routeFilePath is None:
                print("No route file was selected")
                return
            self.sim.changeRoutePath(routeFilePath)
            print("The chosen file was " + routeFilePath)


class Planner:
    connectionString: str
    cursor: None
    connection: None
    simulator: Simulator
    agent: Agent
    scenarioGenerator: ScenarioGenerator

    def __init__(self, connectionString: str, sim: Simulator, agent: Agent):
        self.connectionString = connectionString
        if self.connectionString is not None:
            self.connection, self.cursor = self.dbConnect(self.connectionString)
        self.simulator = sim
        self.agent = agent
        self.scenarioGenerator = ScenarioGenerator("run.sumocfg", sim=self.simulator)

    def dbConnect(self, connectionString: str, host="localhost", port="5432", dbname="quantumleap", username="postgres",
                  password="postgres"):
        if connectionString is not None:
            connection = connectionString
        else:
            connection = "postgres://" + username + ":" + password + "@" + host + ":" + port + "/" + dbname
        with psycopg2.connect(connection) as conn:
            cursor = conn.cursor()
            return conn, cursor

    #Function to create an edgefile with counting vehicles
    def registerOneHourFlow(self, timeslot: str):
        if timeslot is None:
            print("no timeslot was given!")
            return None
        root = ET.Element('data')
        interval = ET.SubElement(root, 'interval', begin='0', end='3600')
        query = "SELECT entity_id, trafficflow, ST_X(location) as lat, ST_Y(location) as lon FROM mtopeniot.etdevice WHERE timeslot LIKE %s;"
        self.cursor.execute(query,  (timeslot,))
        for row in self.cursor.fetchall():
            print(row)
            edge_id = self.getEdgeID(row[2], row[3])
            if edge_id is not None:
                edge = ET.SubElement(interval, 'edge', id=edge_id, entered=str(row[1]))
            print(row)
        tree = ET.ElementTree(root)
        ET.indent(tree, '  ')
        tree.write("edgefile.xml", "UTF-8")

    #Function to get the edgeId starting from the geopoint
    #NOTE: this function is not precise because of the trimming of the coordinates. It's desirable to get edgeID in other ways
    def getEdgeID(self, latitudine: float, longitudine: float):
        lat = general_utils.convert_format(str(latitudine))
        lon = general_utils.convert_format(str(longitudine))
        # Trimming because of the roundings
        lat = lat[:-1]
        lon = lon[:-1]
        df1 = pd.read_csv("../../traffic_loop_dataset/day_flow.csv", sep=',')
        df1["longitudine"] = df1["longitudine"].apply(general_utils.convert_format)
        df1["latitudine"] = df1["latitudine"].apply(general_utils.convert_format)
        matches = df1[df1['longitudine'].str.startswith(lon) & df1['latitudine'].str.startswith(lat)]
        if matches.shape[0] > 1:
            print("Error, there are more roads at these coordinates")
            return None
        return matches.iloc[0]["edge_id"]


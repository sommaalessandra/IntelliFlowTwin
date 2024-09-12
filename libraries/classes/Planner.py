import os
import sys
import psycopg2
from libraries import constants, general_utils
import Simulator
import xml.etree.ElementTree as ET
import pandas as pd
import subprocess


class Planner:
    connectionString: str
    cursor: None
    connection: None
    simulator: Simulator

    def __init__(self, connectionString: str, sim: Simulator):
        self.connectionString = connectionString
        if self.connectionString is not None:
            self.connection, self.cursor = self.dbConnect(self.connectionString)
        self.simulator = sim

    def dbConnect(self, connectionString: str, host = "localhost", port="5432", dbname = "quantumleap", username = "postgres", password = "postgres"):
        if connectionString is not None:
            connection = connectionString
        else:
            connection = "postgres://" + username + ":" +password + "@" + host + ":" + port + "/" + dbname
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
    def getEdgeID(self, latitudine: float,longitudine: float ):
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

    #Function to generate routes starting from an edgefile with counting vehicles
    def generateRoutes(self, edgefile: str, totalVehicles: int, minLoops = 1):
        if edgefile is None:
            print("No edgefile was given")
            return None
        if totalVehicles is None:
            print("The total number of vehicles was not defined")
            return
        if os.path.exists(constants.sumoToolsPath):
            newpath = "../" + constants.simulationPath + "/newSim/"
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            script1 = constants.sumoToolsPath + "/randomTrips.py"
            arg1 = constants.sumoToolsPath + "\\joined_lanes.net.xml"
            subprocess.run(['python', script1, "-n", arg1, "-r", newpath +
                            "sampleRoutes.rou.xml", "--fringe-factor", "10", "--random", "--min-distance",
                            "100", "--random-factor", "200"])
            script2 = constants.sumoToolsPath + "/routeSampler.py"
            subprocess.run([sys.executable,  script2, "-r", newpath + "sampleRoutes.rou.xml",
                            "--edgedata-files", edgefile, "-o", newpath +
                            "generatedRoutes.rou.xml", "--total-count", str(totalVehicles), "--optimize",
                            "full", "--min-count", str(minLoops)])
            print("Routes Generated")

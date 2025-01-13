from libraries.constants import MODEL_DATA_FILE_PATH, SUMO_TOOLS_PATH, SUMO_NET_PATH, SUMO_PATH
from libraries.classes.SumoSimulator import Simulator
import os
import numpy as np
import pandas as pd
import sumolib
from matplotlib import pyplot as plt
import sys
import subprocess

from statistics import mean
import xml.etree.ElementTree as ET

class TrafficModeler:
    """
    A class that manages and compares traffic patterns based on the actual data provided as input

    Attributes:
        trafficDataFile (pandas DataFrame): dataframe containing traffic measurement.
        sumoNet (sumolib.net): sumolib class that contains the road network information representable on SUMO
    """

    trafficData: []
    sumoNet: sumolib.net
    simulator: Simulator
    modelType: str
    date: str
    timeSlot: str
    def __init__(self, simulator: Simulator, trafficDataFile: str, sumoNetFile : str, date: str = None, timeSlot: str = '00:00-23:00', modelType: str = "greenshield"):
        """
        Initializes the TrafficModeler, also deriving road parameters from the SUMO network

        :param trafficDataFile (str): path of the file containing traffic measurement.
        :param sumoNetFile (str): path of the file related to the sumo network (identified with the extension .net.xml).
        :param timeSlot (str): Time window value of the measurements to be evaluated reported in the format hh:mm-hh:mm
        :param modelType (str): Name of the traffic model to apply
        """
        self.simulator = simulator
        trafficDataDf = pd.read_csv(trafficDataFile, sep=';')
        if date is not None:
            trafficDataDf = trafficDataDf[trafficDataDf['data'].str.contains(date)]
            self.date = date
        self.timeSlot = timeSlot
        self.sumoNet = sumolib.net.readNet(sumoNetFile)
        self.modelType = modelType
        self.trafficData = []
        for index, row in trafficDataDf.iterrows():
            edge_id = row["edge_id"]
            edge = self.sumoNet.getEdge(edge_id)
            length = edge.getLength()
            vMax = edge.getSpeed()
            laneCount = len(edge.getLanes())
            vehicleLength = 7.5 #7.5 # this length is including the gap between vehicles
            maxDensity = laneCount / vehicleLength
            print(f"Edge {edge_id}: k_jam = {maxDensity * 1000} vehicles/km")
            first = int(timeSlot[:2])
            last = int(timeSlot[6:8])
            # Calculate the vehicle count for the specified time slot
            if last - first > 1:  # If the time slot spans multiple hours
                total_count = sum(row[f"{hour:02d}:00-{(hour + 1) % 24:02d}:00"] for hour in range(first, last))
                flow = str(total_count)
            else:
                flow = str(row[timeSlot])

            vps = int(flow) / (3600 * (last - first))  # flow is set as vehicles per second
            density = vps / vMax
            laneDensity = density / laneCount
            laneVps = vps / laneCount
            if self.modelType == "greenshield":
                velocity = vMax * (1 - density / maxDensity)
            elif self.modelType == "underwood":
                velocity = vMax * np.exp(density / maxDensity)
            density = vps / velocity if velocity > 0 else maxDensity
            density = density / laneCount
            normVelocity = velocity / vMax
            vpsPerLane = vps / laneCount

            self.trafficData.append({
                "edge_id": edge_id,
                "length": length,
                "laneCount": laneCount,
                "flow": flow,
                "vehiclesPerSecond": vps,
                "vpsPerLane": vpsPerLane,
                "laneVps": laneVps,
                "density": density,
                "laneDensity": laneDensity,
                "maxDensity": maxDensity,
                "vMax": vMax,
                "velocity": velocity,
                "normVelocity": normVelocity
            })



    def saveTrafficData(self, outputDataPath: str = MODEL_DATA_FILE_PATH):
    # TODO: set a name convention for saving new model data (e.g. greenshield_01-02-2024_00:00-23:00)
        """
        Save current traffic information stored inside the TrafficModeler into a .csv file
        Args:
            outputDataPath: path of the file to save the traffic model data
        """
        print("Saving...")
        df = pd.DataFrame(self.trafficData)
        df.to_csv(outputDataPath, sep=';', index=False, float_format='%.4f', decimal=',')
        print("New Model data saved into: " + outputDataPath + " file")

    # TODO: plotModel should also report some values for similarity
    def plotModel(self, model: str):
        """
        function that plots the values of flux, density and velocity against each other in three graphs.
        The values are compared with the traffic model chosen at the initialization stage
        """
        print("Plotting the data according to theoretical model...")
        if model is None:
            df = pd.DataFrame(self.trafficData)
        else:
            df = pd.read_csv(model)
        # unique values of max speed
        unique_vmax = df["vMax"].unique()

        # Crea tre figure per i tre tipi di plot
        fig1, ax1 = plt.subplots(len(unique_vmax), 1, figsize=(8, 4 * len(unique_vmax)))
        fig2, ax2 = plt.subplots(len(unique_vmax), 1, figsize=(8, 4 * len(unique_vmax)))
        fig3, ax3 = plt.subplots(len(unique_vmax), 1, figsize=(8, 4 * len(unique_vmax)))

        if len(unique_vmax) == 1:  # Garantisci che gli assi siano array anche con un solo vmax
            ax1 = [ax1]
            ax2 = [ax2]
            ax3 = [ax3]

        for i, v_max in enumerate(unique_vmax):
            # Filtra i dati per v_max corrente
            subset = df[df["vMax"] == v_max]
            v_max = (v_max * 3.6).round()
            # Calcola k_jam per ogni segmento basandosi sul numero di corsie
            # Media i valori di lane_count se ci sono più segmenti con lo stesso v_max
            avg_lane_count = subset["laneCount"].mean()
            # k_jam = 200 / avg_lane_count  # Stima densità al blocco
            # k_jam = 133 / 1000  # Densità massima (esempio: 133 veicoli/km)
            k_jam = avg_lane_count / 7.5  # Densità massima (esempio: 133 veicoli/km)
            # Dati di densità teorici (da 0 a k_jam)
            k = np.linspace(0, k_jam, 500)

            if self.modelType == "greenshield":
                v_theoretical = v_max * (1 - k / k_jam)
            elif self.modelType == "underwood":
                v_theoretical = v_max * np.exp(k / k_jam)
            q_theoretical = v_theoretical * k  # Flusso teorico

            # Flusso osservato
            q_observed = subset["velocity"] * 3.6 * subset["density"]

            # Plot Velocità-Densità
            ax1[i].plot(k, v_theoretical, label=f"Curva teorica v_max = {v_max} km/h", color='blue')
            ax1[i].scatter(subset["density"], (subset["velocity"] * 3.6), label="Dati osservati", color='orange',
                           alpha=0.7)
            ax1[i].set_title(f"Velocità-Densità (v_max = {v_max} km/h)")
            ax1[i].set_xlabel("Densità (veicoli/km)")
            ax1[i].set_ylabel("Velocità (km/h)")
            ax1[i].legend()
            ax1[i].grid()

            # Plot Flusso-Densità
            ax2[i].plot(k, q_theoretical, label=f"Curva teorica v_max = {v_max} km/h", color='green')
            ax2[i].scatter(subset["density"], q_observed, label="Dati osservati", color='red', alpha=0.7)
            ax2[i].set_title(f"Flusso-Densità (v_max = {v_max} km/h)")
            ax2[i].set_xlabel("Densità (veicoli/km)")
            ax2[i].set_ylabel("Flusso (veicoli/h)")
            ax2[i].legend()
            ax2[i].grid()

            # Plot Flusso-Velocità
            ax3[i].plot(v_theoretical, q_theoretical, label=f"Curva teorica v_max = {v_max} km/h", color='purple')
            ax3[i].scatter((subset["velocity"] * 3.6), q_observed, label="Dati osservati", color='brown', alpha=0.7)
            ax3[i].set_title(f"Flusso-Velocità (v_max = {v_max} km/h)")
            ax3[i].set_xlabel("Velocità (km/h)")
            ax3[i].set_ylabel("Flusso (veicoli/h)")
            ax3[i].legend()
            ax3[i].grid()

        # Migliora il layout delle figure
        fig1.tight_layout()
        fig2.tight_layout()
        fig3.tight_layout()

        # Mostra tutte le figure
        plt.show()

    def setModel(self, newModelType):
    # TODO: changing the model type can be useful when comparing different models with same data. It requires to iter
    # through all the measurement dataset
        print("Function to be done")

    def evaluateModel(self, detectorFilePath, detectorOutputSUMO: str, outputFilePath: str):
    # TODO: evaluate model according to SUMO output
        print("Function to be done")

        # Parse detector.add.xml
        tree = ET.parse(detectorFilePath)
        root = tree.getroot()

        # Estrarre il mapping detector -> edge
        detector_mapping = {}
        for detector in root.findall('inductionLoop'):
            detector_id = detector.get('id')
            lane = detector.get('lane')  # Es. "23276104_0"
            edge_id = lane.split('_')[0]  # Ottieni solo l'edge_id
            detector_mapping[detector_id] = edge_id

        parser = ET.XMLParser(encoding='UTF-8')
        tree = ET.parse(detectorOutputSUMO, parser=parser)
        root = tree.getroot()
        detectorData = []
        for interval in root.findall("interval"):
            detector_id = interval.get('id')
            edge_id = detector_mapping[detector_id]
            flow = float(interval.get('flow'))
            speed = float(interval.get('speed'))
            if flow > 0:
                detectorData.append({
                    'id': detector_id,
                    'edge_id': edge_id,
                    'flow': flow,
                    'meanSpeed': speed,
                    'occupancy': float(interval.get('occupancy'))
                })

        detector_df = pd.DataFrame(detectorData)
        # detector_df.to_csv(outputFilePath, sep=';')
        model_df = pd.DataFrame(self.trafficData)

        # Confronta il modello con i detector per ID
        merged_df = pd.merge(model_df, detector_df, left_on='edge_id', right_on='edge_id', how='inner')

        # Calcola le discrepanze
        merged_df['flow_diff'] = merged_df['flow_x'].astype(int) - merged_df['flow_y'].astype(int)
        merged_df['velocity_diff'] = merged_df['velocity'] - merged_df['meanSpeed']
        merged_df.to_csv(outputFilePath, sep=';', float_format='%.4f', decimal=',')
        print(merged_df[['edge_id', 'flow_diff', 'velocity_diff']])


    def vTypeGeneration(self, modelType: str):
        """

        """

        # Funzione per aggiungere un calibrator
        def add_calibrator(root, calibrator_id, edge, pos, type, output, flows):
            calibrator = ET.SubElement(root, "calibrator", {
                "id": calibrator_id,
                "edge": edge,
                "pos": pos,
                "type": type,
                "output": output
            })
            for flow in flows:
                ET.SubElement(calibrator, "flow", flow)

        if modelType == "idm":
            carFollowModel = "IDM"
            vtypeID = "customIDM"
            lane_densities = [item['density'] for item in self.trafficData]
            velocities = [item['velocity'] for item in self.trafficData]
            spaceBetweenVehicles = 1 / mean(lane_densities)
            carLength = 5
            freeSpace = spaceBetweenVehicles - carLength
            reactionTime = freeSpace / mean(velocities)

            folder_name = f"{self.date}_{self.modelType}"
            folder_path = os.path.join(SUMO_PATH, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            # Nome del file XML
            output_file = os.path.join(folder_path, "vtype.add.xml")
            # Creazione della struttura XML
            root = ET.Element("additional")  # Elemento radice
            vtype = ET.SubElement(root, "vType", {
                "id": vtypeID,
                "carFollowModel": carFollowModel
                # "tau": str(reactionTime)
            })
            df = pd.DataFrame(self.trafficData)
            for index, row in df.iterrows():
                flow=[{"begin": "0" , "end": "3600", "vehsPerHour": str(row['flow']), "speed": str(row['velocity'])}]
                add_calibrator(root, calibrator_id="calibrator_"+str(index), edge=row['edge_id'], pos="0", type=vtypeID , output="calib_out.xml",
                               flows=flow)
            # Scrittura su file
            tree = ET.ElementTree(root)
            # output_file = "vtype.add.xml"
            ET.indent(tree, '  ')
            tree.write(output_file, encoding="utf-8", xml_declaration=True)
            print(f"vType File created: {output_file}")


    def generateRandomRoute(self, sumoNetPath: str):

        folder_name = f"{self.date}_{self.modelType}"
        folder_path = os.path.join(SUMO_PATH, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        script = SUMO_TOOLS_PATH + "/randomTrips.py"
        subprocess.run(['python', script, "-n", sumoNetPath, "-r", folder_path + "/sampleRoutes.rou.xml",
                        "--fringe-factor", "10", "--random", "--min-distance", "100", "--random-factor", "200"])
    def generateRoute(self, inputEdgePath: str, inputRoutePath: str, outputRoutePath: str, modelType: str, withInitialRoute = True):
        if withInitialRoute:
            self.generateRandomRoute(sumoNetPath=SUMO_NET_PATH, outputRoutePath=SUMO_PATH)
        folder_name = f"{self.date}_{self.modelType}"
        folder_path = os.path.join(SUMO_PATH, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        outputRoutePath = folder_path + "/generatedRoutes.rou.xml"
        script = SUMO_TOOLS_PATH + "/routeSampler.py"
        # attributes = --attributes="type=\"idmAlternative\""
        subprocess.run([sys.executable, script, "--r", inputRoutePath,
                        "--edgedata-files", inputEdgePath, "-o", outputRoutePath, "--edgedata-attribute", "qPKW",
                        "--write-flows", "number"])
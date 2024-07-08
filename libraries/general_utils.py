import os
import pandas as pd
import string
import secrets
from datetime import datetime

def reading_files(folder):
    files = os.listdir(folder)
    data = {}
    for i, file in enumerate(files):
        file_path = os.path.join(folder, file)
        key = os.path.splitext(file)[
            0]  # remove .csv extension to use file name as key value to access the data dictionary
        data[key] = pd.read_csv(file_path)
        files[i] = key
    return data, files

def generate_random_key(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def load_env_var(file_path):
    env_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # remove whitespace
            if line and not line.startswith('#'):  # line is not a comment
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()  # removing leading or trailing spaces
    return env_vars

# function to calculate difference between actual and previous date time of dataset entries to properly simulate devices
def delay_calculation(actual_datetime, last_datetime):
    if last_datetime == -1:
        last_datetime = actual_datetime
    delta = int((actual_datetime - last_datetime).total_seconds()) / 100000
    last_datetime = actual_datetime

    return delta, last_datetime


# TODO: handle multiple hours time-slots in such a way that the sending of data is proportional
#  to the time of the measurement
def processingTlData(trafficData, trafficLoop):
    # for key, values in trafficData.items():
        # iterate through registered devices
        for ind, device in trafficLoop.items():
            # look for sensor belonging to device (only one in the traffic loop case)
            for sensor in device.sensors:
                if sensor.name == "TFO":
                    tl = trafficData.loc[trafficData["ID_loop"] == int(sensor.device_partial_id)]
                    flow = tl["flow"].values[0]
                    coordinates = str(tl["geopoint"].values[0])
                    direction = str(tl["direction"].values[0])
                    sensor.send_data(flow, coordinates, direction,device_id=sensor.device_partial_id, device_key=sensor.api_key)


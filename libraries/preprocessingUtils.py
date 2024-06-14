import pandas as pd
import csv
import xml.etree.ElementTree as ET
import datetime
from libraries.constants import *
def filter_roads(input_file, road_file, output_file = 'filtered_output.csv', input_column = 'Nome via', filter_column = 'nome_via'):
    """
    The function filters a traffic input file based on the road names. The input_column and filter_column must be
    specified to match the values of the road names between the input file and the road_file. The result will be written
    in the given output file. Unused roadnames inside the filter will be printed.
    """
    # Create a set of road names from the road file
    filter_roadnames = set()
    with open(road_file, 'r', newline='', encoding='utf-8') as csvfile_filter:
        reader_filter = csv.DictReader(csvfile_filter, delimiter=';')
        # Check if filter column exist inside the road_file
        if filter_column not in reader_filter.fieldnames:
            print("Error: column 'nome_via' not found inside the road file.")
            return
        for row in reader_filter:
            # Add column value to the filter set
            filter_roadnames.add(row[filter_column].lower())

    # Filter input file based on road names collected
    filtered_rows = []
    # List of road names in the input file
    input_roadnames = set()
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile_input:
        reader_input = csv.DictReader(csvfile_input, delimiter=';')
        headers = reader_input.fieldnames  # Ottieni gli header
        filtered_rows.append(headers)
        for row in reader_input:
            road_name = row[input_column].lower()
            input_roadnames.add(row[input_column].lower())
            # Add row if the road name is in the filter set
            if road_name in filter_roadnames:
                filtered_rows.append([row[col] for col in headers])

    # Write the result in the csv output file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile_output:
        writer = csv.writer(csvfile_output, delimiter=';')
        writer.writerows(filtered_rows)
        print("Filtered output created. ")

    unmatched_roadnames = filter_roadnames - input_roadnames
    # Print umatched roadnames
    print("Unused road names in the filter:")
    for voce in unmatched_roadnames:
        print(voce)
    print("The numer of unmatched road names is: " + str(len(unmatched_roadnames)))


def filter_with_accuracy(file_input, file_accuracy, date_column='data', sensor_id_column='codice_spira', output_file='accurate_output.csv', accepted_percentage=90):
    """
    The function filters the dataset using accuracy information. Both files must have the date and the ID of the sensor
    to be filtered properly. A threshold percentage can be provided to only accept the measurement above that value.
    """
    df1 = pd.read_csv(file_input, sep=';', encoding="UTF-8")
    df_acc = pd.read_csv(file_accuracy, sep=';', encoding="UTF-8")
    # Filtering the accuracy file to only have measurements above the accepted_percentage
    for ind, column in enumerate(df_acc.columns):
        if ind > 1:
            df_acc[column] = df_acc[column].str.replace('%', '')
            df_acc = df_acc.drop(df_acc[df_acc[column].astype(int) < accepted_percentage].index)
    # Filtering the file_input by matching it with the filtered accuracy file
    identifier = df_acc[[date_column, sensor_id_column]]
    keys = list(identifier.columns.values)
    i1 = df1.set_index(keys).index
    i2 = df_acc.set_index(keys).index
    df = df1[i1.isin(i2)]
    df.to_csv(output_file, sep=';')
    print("Output with filtered accuracy created. ")

def link_roads_IDs(file_input, road_file_ids, output_file = 'final.csv' ,input_roadname_column = 'Nome via', direction_column = 'direzione', roadname_column = 'nome_via'):
    """
    The function adds the road IDs based on the road file given as a new column in the input file. The entries in the
    input file must have a direction (expressed using direction_column) in order to be linked with the right lane ID of
    the road.
    """
    df1 = pd.read_csv(file_input, sep=';')
    # Dropping entries without a direction
    df1 = df1.dropna(subset=[direction_column])
    df1["edge_id"] = "unknown"
    df2 = pd.read_csv(road_file_ids, sep=';')
    df2['nome_via'] = df2[roadname_column].str.lower()
    df1 = df1.reset_index()  # make sure indexes pair with number of rows
    for index, row in df1.iterrows():
        roadname = row[input_roadname_column].lower()
        direction = row[direction_column]
        # check if direction is multiple (e.g. SW for South-West)
        if len(direction) > 1:
            direction1 = direction[:1]
            direction2 = direction[1:]
            matched_row = df2[df2[roadname_column].str.contains(roadname) & (df2[direction_column].str.contains(direction1) | df2[direction_column].str.contains(direction2))]
        else:
            matched_row = df2[df2[roadname_column].str.contains(roadname) & df2[direction_column].str.contains(direction)]
        df1.at[index, 'edge_id'] = matched_row['edge_id'].values
    df1.to_csv(simulationPath + output_file, sep=';')
    print("Created Output file with Road IDs linked")

def generate_edgedata_file(input_file, output_file = 'edgedata.xml' ,date = "01/02/2024", time_slot = "00:00-01:00",duration = '3600'):
    """
    The function generate the XML edgedata file useful for the route sampler in Eclipse SUMO. Each row in the input file
    must have an edge id, a date and a time_slot in which the number of vehicles are reported.
    """
    root = ET.Element('data')
    interval = ET.SubElement(root, 'interval', begin='0', end=duration)
    df1 = pd.read_csv(input_file, sep=';')
    df1 = df1[df1['data'].str.contains(date)]
    for index, row in df1.iterrows():
        edge_id = str(row['edge_id'])
        first = int(time_slot[0:2])
        last = int(time_slot[6:8])
        # check if time window is two hours long
        if last - first > 1:
            time_slot1 = str(datetime.time(first).strftime("%H:00"))+'-'+str(datetime.time(first+1).strftime("%H:00"))
            time_slot2 = str(datetime.time(last-1).strftime("%H:00"))+'-'+str(datetime.time(last % 24).strftime("%H:00"))
            count = str(row[time_slot1] + row[time_slot2])
        else:
            count = str(row[time_slot])
        edge = ET.SubElement(interval,'edge', id=edge_id, entered=count)
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(simulationPath + output_file, "UTF-8")

# TODO
def link_origin_destination(file_input, file_road_id):
    print("prova")

#This method is used to filter the file before using it inside the DT platform
def filter_day(input_file, output_file = 'day_flow.csv', date = "01/02/2024"):
    df1 = pd.read_csv(input_file, sep=';')
    df1 = df1[df1['data'].str.contains(date)]
    df1 = df1[["00:00-01:00","edge_id", "geopoint", "direzione"]]
    df1.to_csv(simulationPath + output_file, sep=',')

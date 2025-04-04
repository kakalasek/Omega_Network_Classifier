#!/usr/bin/env python3

import pytrap
import sys
import pandas as pd
import numpy as np
import pickle
import json

# Setup -------------------------------

trap = pytrap.TrapCtx()
trap.init(sys.argv, 1, 1)

inputspec = "time TIME_FIRST,ipaddr DST_IP,ipaddr SRC_IP,int8* PPI_PKT_DIRECTIONS,uint16* PPI_PKT_LENGTHS"
trap.setRequiredFmt(0, pytrap.FMT_UNIREC, inputspec)
rec = pytrap.UnirecTemplate(inputspec)

outputspec = "time TIME_FIRST,ipaddr DST_IP,ipaddr SRC_IP,string CLASS"
output = pytrap.UnirecTemplate(outputspec)
trap.setDataFmt(0, pytrap.FMT_UNIREC, outputspec)

output.createMessage()

class_mapping = {}

with open("classes/classes_mapping.json", "r") as file:
    class_mapping =  json.load(file)

loaded_model = pickle.load(open('models/network_classifier_cesnet_hgbt.dat', 'rb'))

# Methods ---------------------------------

def do_classification(rec):
    """Classifies the flow and sends data to trap output

    Args:
        rec (UnirecTemplate): Contains all the data needed to perform the classification
    """
    
    if len(rec.PPI_PKT_LENGTHS) > 0:

        packets_length_times_direction = np.array(rec.PPI_PKT_DIRECTIONS) * np.array(rec.PPI_PKT_LENGTHS)
        packets_length_times_direction = np.resize(packets_length_times_direction, 30)
        packets_length_times_direction = packets_length_times_direction.reshape(1, -1)

        features = pd.DataFrame(packets_length_times_direction, columns=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29'])

        prediction = str(loaded_model.predict(features).tolist()[0])

        traffic_class = class_mapping[prediction]

        output.TIME_FIRST = rec.TIME_FIRST
        output.SRC_IP = rec.SRC_IP
        output.DST_IP = rec.DST_IP
        output.CLASS = traffic_class

        trap.send(output.getData(), 0)

# Main loop -----------------------------------

while True:
    try:
        data = trap.recv()
    except pytrap.FormatChanged as e:
        fmttype, inputspec = trap.getDataFmt(0)
        rec = pytrap.UnirecTemplate(inputspec)
        data = e.data
    if len(data) <= 1:
        break

    rec.setData(data)

    do_classification(rec)


trap.finalize()

#!/usr/bin/env python3

import pytrap
import sys
import json
import yaml
import os
from ipaddress import ip_address

def aggregate(rec, agg_dict: dict, write: int, agg_file: str):
    """This function aggregates the flow data into one dictionary file

    Args:
        rec (UnirecTemplate): Contains all the data needed for aggregation
        agg_dict (dict): The dictionary which is used for aggregation
        write (int): If the dictionary should be written to file
        agg_file (str): The path of the aggregation file
    """

    ipaddr = str(rec.SRC_IP) if ip_address(str(rec.SRC_IP)).is_private else str(rec.DST_IP)
    service = str(rec.CLASS)

    if ipaddr in agg_dict.keys():
        if service in agg_dict[ipaddr].keys():
            agg_dict[ipaddr][service] += 1
        else:
            agg_dict[ipaddr][service] = 1
    else:
        agg_dict[ipaddr] = {}
        agg_dict[ipaddr][service] = 1

    if write:
        with open(agg_file, "w") as file:
            json.dump(agg_dict, file)
        

with open("config.yaml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

if not isinstance(cfg["write"], int):
    raise SystemExit("You must specify 'write' as a positive integer")
try:
    with open(cfg["filepath"], "w") as file:
        file.write("")
except:
    raise SystemExit("The specified file is not valid")

outputfile = cfg["filepath"]

trap = pytrap.TrapCtx()
trap.init(sys.argv, 1, 0)

inputspec = "ipaddr SRC_IP,ipaddr DST_IP,string CLASS"
trap.setRequiredFmt(0, pytrap.FMT_UNIREC, inputspec)
rec = pytrap.UnirecTemplate(inputspec)

json_agg = {}
write = cfg["write"]

# Main loop

print("Aggregation has started")

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

    write -= 1

    aggregate(rec, json_agg, write <= 0, outputfile)

    if write <= 0:
        print("Data written")
        write = cfg["write"]

trap.finalize()

    
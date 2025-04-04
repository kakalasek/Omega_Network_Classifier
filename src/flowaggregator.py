#!/usr/bin/env python3

import pytrap
import sys
import json
import yaml
import signal
from ipaddress import ip_address

# Methods ----------------------

def aggregate(rec, agg_dict: dict, write: bool, agg_file: str):
    """This function aggregates the flow data into one dictionary file

    Args:
        rec (UnirecTemplate): Contains all the data needed for aggregation
        agg_dict (dict): The dictionary which is used for aggregation
        write (bool): If the dictionary should be written to file
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
        
# Setup ---------------------------------
with open("config.yaml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

if not isinstance(cfg["write"], int):
    print("The 'write' configuration variable needs to be a number")
    sys.exit(1)
elif cfg["write"] <= 0:
    print("The 'write' configuration variable needs to be greater than zero")
    sys.exit(1)

try:
    with open(cfg["filepath"], "w") as file:
        file.write("")
except:
    print("The 'filepath' configuration variable needs to be a valid filepath")
    sys.exit(1)

outputfile = cfg["filepath"]

trap = pytrap.TrapCtx()
trap.init(sys.argv, 1, 0)

inputspec = "ipaddr SRC_IP,ipaddr DST_IP,string CLASS"
trap.setRequiredFmt(0, pytrap.FMT_UNIREC, inputspec)
rec = pytrap.UnirecTemplate(inputspec)

json_agg = {}
write = cfg["write"]

# Main loop --------------------------------------------

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

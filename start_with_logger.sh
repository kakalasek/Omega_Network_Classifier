#!/bin/bash

set -e

if [ -z $1 ]; then
    echo "You have to provide an interface to listen to"
    exit 2
fi

cd src

sudo ipfixprobe -i "raw;ifc=$1" -p "pstats" -p "tls" -o "unirec;i=u:mysocket:timeout=WAIT;p=(pstats,tls)" &
/usr/bin/nemea/unirecfilter -F 'port == 443' -i u:mysocket,u:filtered &
./flowclassifier.py -i u:filtered,u:logged &
/usr/bin/nemea/logger -i u:logged -t
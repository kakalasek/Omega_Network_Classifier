#!/bin/bash

set -eE

if [ -z $1 ]; then
    echo "You have to provide an interface to listen to"
    exit 2
fi

started_processes=$(mktemp)

cleanup() { 
    while read pid; do
        kill "$pid" 2>/dev/null
        echo "Killed process $pid"
    done < "$started_processes"
    rm -f "$started_processes" 
    exit 0
}

trap cleanup TERM INT ERR

cd src

ipfixprobe -i "raw;ifc=$1" -p "pstats" -p "tls" -o "unirec;i=u:mysocket:timeout=WAIT;p=(pstats,tls)" &
echo $! >> $started_processes

/usr/bin/nemea/unirecfilter -F 'port == 443' -i u:mysocket,u:filtered &
echo $! >> $started_processes

./flowclassifier.py -i u:filtered,u:logged &
echo $! >> $started_processes

/usr/bin/nemea/logger -i u:logged -t

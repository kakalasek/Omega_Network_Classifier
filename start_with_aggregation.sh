#!/bin/bash

set -e

if [ -z $1 ]; then
    echo "You have to provide an interface to listen to"
    exit 2
fi

cd src

ipfixprobe -i "raw;ifc=$1" -p "pstats" -p "tls" -o "unirec;i=u:mysocket:timeout=WAIT;p=(pstats,tls)" &
p1=$!

/usr/bin/nemea/unirecfilter -F 'port == 443' -i u:mysocket,u:filtered &
p2=$!

./flowclassifier.py -i u:filtered,u:logged &
p3=$!

trap "
    echo killing $p1 $p2 $p3
    kill $p1
    kill $p2
    kill $p3
    exit 0
" TERM INT

./flowaggregator.py -i u:logged
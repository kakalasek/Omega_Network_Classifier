#!/bin/bash

set -e

dnf install -y dnf-plugins-core

dnf copr -y enable @CESNET/NEMEA-stable
dnf copr -y enable @CESNET/NEMEA-testing

dnf install -y epel-release
dnf config-manager -y --enable ol9_developer_EPEL
dnf config-manager -y --set-enabled ol9_codeready_builder

dnf install -y \
    git \
    libatomic \
    libunwind-devel \
    dpdk-devel \
    autoconf \
    automake \
    libtool \
    pkgconfig \
    make \
    gcc \
    gcc-c++ \
    kernel-devel

dnf install -y nemea-framework-devel
dnf install -y nemea-modules
dnf install -y lz4-libs
dnf install -y lz4-devel
dnf install -y libpcap-devel 
dnf install -y fuse3-devel
dnf install -y telemetry
dnf install -y python

git clone --recurse-submodules https://github.com/CESNET/ipfixprobe
cd ipfixprobe
autoreconf -i
./configure --with-pcap --with-nemea
make
make install

dnf install -y ipfixprobe

dnf install -y pip

pip install pandas
pip install scikit-learn

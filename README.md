---
title: Pipuv-Network-Classifier
author: Josef Vetrovsky
date: 5. 5. 2025
school: SPSE Jecna
---

# About

This simple network classifier tightly works with the NEMEA framework by CESNET. It provides several different models to accomplish the task. By default, the best one is chosen.           
It simply classifies 443 services only by first 30 packets from the communication.

# Directory Structure

The **top directory** contains the setup and start application scripts         
The **jupyter_scripts** directory contains the jupyter notebooks for training the model and processing of the data. It also contains two json files, *classes_mapping.json* and *classes.json*. The first file contains mapping of every class in this format *class_number: class_name*. The second containes containes keyword and classes to map to that keywords in this format *keyword: class_name*.              
The **src** directory contains all the modules, models and also, for practical reasons, a copy of *classes.json* file. This file is used to convert the numerical prediction a to particular service. It is here, because the file path is more practical for the modules. All the models are in the *models* directory;

Some models are too big for Github. Also some data may also be too big. I have thus put it onto this Google drive: https://drive.google.com/drive/folders/1XcOfXqXIrEK_SFA2j5aLiGlSPVSBf_c2?usp=drive_link          

You can download all the models and some datasets there. I purposefully have not included the CESNET dataset in order to keep it secret.

## Datasets

Two different datasets were used to train the models.           
First dataset is made up of **aggregated network captures from family members, friends and myself**. It is not so effective, but because the amount of data is not so great, the models could be trained in fair amount of time. It also cant really classify all the classes, simply because the data does not involve that many services. *12 343 rows*.            
The second dataset is **a very large file of network flows from CESNET**. This dataset was annonymized before, so no IP addresses are present. It contains larger amount of different services and data in general. The best models offered are trained on this dataset. *1 031 097 rows*.

## Dataset processing

1. **Extract our desired columns**      
    There is a lot of column in the datasets, which were not needed. Only packet sizes and directions of the first 30 packets in each flow and TLS_SNI field were extracted. The TLS_SNI field contains a value used for annotation.
2. **Remove duplicates and flow without any packets**           
    Duplicates are removed using basic Pandas functions and every flow with first packet size set to 0 (or first packet direction set ot None, it is the same) is dropped
3. **Select only packets with DST_PORT with the value 443**
    We are interested mainly in web services, which are accessible on port 443. So to filter out unneccesary DNS and stuff, we have to only pick the data on this port.
4. **Multiply packet directions and sizes**           
    In order to reflect the packet direction in the dataset, we need to multiply the values from the packet directions list with the packet sizes.
5. **Append TLS_SNI to the multiplied values**
6. **Create the classes**           
    Define the classes. This is done by creating a simple dictionary, where keys are the string we will search for in the TLS_SNI field and values are the service names. A new column names *class* is defined and every value there is set to the *other* service class. Then a simple algorthim will try to find every key in the dataset and if it sees the key string inside the TLS SNI field, it will replace the *other* class with the value assigned to the the particular key inside the dictionary.         
7. **Transform classes into numbers**           
    A simple dictionary mapping is created, which will be used for resolving the predictions of the models. Then, according to this dictionary, the *class* column values are replaced with the numbers

## Model training

Several models are available in this application. There is also an option to choose a model, but by default the best in testing is picked.          
The models have a naming scheme, which looks like this:

    network_classifier_<cesnet/home>_<algorithm_shortname>.dat

**Dataset**     
**cesnet** refers to the CESNET dataset, which was used for training.           
**home** refers to the dataset aquired from home e. i. from my network data and network data of my relatives and friends

**Model type**      
Here is a table of shortnames for different models:

| Shortname | Model |
|-----------|-------|
| rf        | Random Forest Clasifier |
| gbt       | Gradient Boosting Classifier |
| hgbt      | Hist Gradient Boosting Classifier |

## Data shape

The final dataset is composed of 31 columns one of which is used for annotation.            
Columns 1 - 29 look the same, so only some are shown here. They are the sizes of first 30 packets. The difference between a negative and positive value is the direction of the packet relative to the src IP within the flow.          
The class here is represented by a string, but before training it needs to be converted into different numbers (one for each class)

| 0 | 1 | 2 | ... | 29 | class |
|---|---|---|-----|----|-------|
|517|-30|-30| ... |0   | gmail |
|20 |20 |-90| ... |-200| github|

# Models

I will list all available models here, their score and the way the score was calculated. The chosen hyperparameters are also listed.

| name | score | method | hyperparamameters |
|------|-------|--------|-------------------|
| network_classifier_cesnet_ghbt.dat | 0.9517214625157598 | score() method from Scikit-learn | *max_iter*: 600<br>*max_leaf_nodes*: 31 |
| network_classifier_home_ghbt.dat | 0.9149797570850202 | score() method from Scikit-learn | *max_iter*: 100<br>*max_leaf_nodes*: 15 |
| network_classifier_home_gbt.dat | 0.9732793522267207 | score() method from Scikit-learn | *max_depth*: 8<br>*n_estimators*: 300<br>*subsample*: 0.9 |
| network_classifier_home_rf.dat | 0.968421052631579 | score() method from Scikit-learn | *estimator__max_depth*: None<br>*min_samples_leaf*: 1<br>*min_samples_split*: 2<br>*n_estimators*: 600 |

# How to setup

This software is tested only on **Oracle Linux 9.3 and 9.5**.     
NEMEA needs an rpm based distribution in order to work properly and be setup easily.

## Requirements

**Git**, so you can clone the repo. The rest is done by the setup script.

## Prepare our VM

Simply run:

```Bash
sudo ./setup_vm.sh
```

This script will download all the needed packages and download and install ipfixprobe for you

## Run with simple logger

One of the provided scripts will start the application, which will simply log every classified packet to the screen terminal        
We also need to specify the network interface we want to monitor             
After setting up our vm, we can run:

```Bash
./start_application_logger.sh <network_interface_name>
```

Since starting Ipfixprobe needs sudo privileges, you will be asked to enter your password. Then you will probably need to wait a while until the system starts to log something, since Ipfixprobe first needs to catch some packets in order to return some flows.              
After some time the system should start to log in this format: *TIMESTAMP,DST_IP,SRC_IP,CLASS*

## Run with network aggregator

### Configuration

There is a file called config.yaml under the src directory.         
You can configure **write** there. That is how often will the aggregator write to the file. More specifically, after it recieves how many packet flows.             
There is also **filepath**, which is the path to a file you want to save the outputs to.

### Start

Then just do:

```Bash
./start_flowaggregator.sh
```

### Exceptions and errors

You can enter invalid data into the config file. The script will simply tell you and force you to rewrite them

# Application diagram

Since NEMEA framework is based on microservices, also this project uses such a concept. Several NEMEA modules are connected together with unix sockets. At the end we have a special kind of module, which either does something with the classification or simply logs the data using the logger module.

![Diagram](omega_picture.svg)

The first module listens to an interface, creates flows from packets and returns the data in certain format.            
The unirec filter filters out all unneccessary data. We are only interested in services over port 443.           
Finally, our classifier classifies the flow and sends it to another unix socket.             
That final socket can be caught by a logger or any other specialized module.

# 3d-party libraries

Cesnet NEMEA - https://github.com/CESNET/Nemea              
Cesnet Ipfixprobe - https://github.com/CESNET/ipfixprobe                
Nemea-pytrap and all other modules used are also part of the NEMEA project

# Sources

Cesnet NEMEA documentation on Github - https://github.com/CESNET/Nemea          
Cesnet Ipfixprobe documentation on Github - https://github.com/CESNET/Nemea                
Cesnet Ipfixprobe documentation on Github Pages - https://cesnet.github.io/ipfixprobe/          
Cesnet Nemea-pytrap documentation - https://nemea.liberouter.org/doc/pytrap/index.html          
All other modules used are also a part of the NEMEA project       
Training script for decision tree algorithms from Mgr. Mykyta Narusevych - *I decided not to publish this script here*         
Scripts from Python for Data Science course from Netacad FEL - *I cant publish those scripts here*

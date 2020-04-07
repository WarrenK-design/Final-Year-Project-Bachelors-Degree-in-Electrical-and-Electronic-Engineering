#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 01/04/2020

##Decription##
# This script is used as a configuration script to be run when the openHAB session starts
# The function of this script is to:
#   1. Log the hub data to the "hub" table in the community_grid database
#   2. Log the things set up in openHAB to the "Devices" table in the community_grid database
#   3. Log the items setup in openHAB to the "Items" table in the community_grid database
#   4. Write the config.json file for the configuration of what devices a script controls  

## Modules to import ##
# sys          - Used to navigate directorys in python 
# open_HAB     - Contains the open_HAB Class with functions for interfacing with openHAB
# smart_meters - Contains functions for interfacing with modubus meters 
# datetime     - Used for getting time in python 
# logging      - Used to log to log file
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.open_HAB import open_HAB
from openHAB_Proj import smart_meters
from openHAB_Proj.AeotechZW096 import AeotechZW096
from datetime import datetime
import logging
import os
import pprint
import json

##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/config.log') #Get a file handler
file_handler.setFormatter(formatter)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)
#os.chmod('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/config.log', 0o777)




##The process##
#Intitialse an opeb_HAB object 
obj = open_HAB()
#Log the hub data to the "hub" table
obj.initialise_hub_data()
#Get the things configured in open_HAB setup
obj.get_things()
#Sort the items based on brand type (Currently only using AeotechPlug, reading the smartMeter in Python)
obj.sort_AeotechZW096()

#Loop through each of the devices found 
if obj.AeotechZW096things is not None:
    for key, plug in obj.AeotechZW096things.items():
        if (plug.status['status']) != "ONLINE":
            logger.warning(f"{plug.UID} is offline not including in config file")
        else:
            plug.turn_on()
            #Log to the "Devices" table in community_grid
            plug.update_devices_data()
            #Log to the "items" table in community_grid
            plug.update_items_data()
            #Write the configuration file for controlling the scripts
            plug.write_config(plug.switch['UID'],plug.UID,'/home/openhabian/Environments/env_1/openHAB_Proj/lib')
logger.info("Start Up Script Executed")
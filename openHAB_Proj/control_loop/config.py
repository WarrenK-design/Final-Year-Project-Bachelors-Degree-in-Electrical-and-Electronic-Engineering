#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 08/05/2020

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
# AeotechZW096 - Class which contains the functionality for the smart plugs
# MySQL        - Module which contains the functionality for interacting with SQL database 
# datetime     - Used for getting time in python 
# logging      - Used to log to log file
# os           - USed to see if the processes are still running of control loop 
# json         - Writes and read to the process_list.json file in the lib directory 
# asyncio      - Implments Asynchrounous function calls within Python 
# subprocess   - Used to change the permissions on the process_list.json file 
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.open_HAB import open_HAB
from openHAB_Proj import smart_meters
from openHAB_Proj.AeotechZW096 import AeotechZW096
from openHAB_Proj import MySQL
from datetime import datetime
import logging
import os
import json
import asyncio
import subprocess

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

##check_process##
# The purpose of this function is to check if a process is running in the background
# The process PID's are held in a json file for the control scripts
# Need to read in the JSON file
# Check if the process is currently running 
# If it is running do not launch it agaian
# If it is not runnning then launch it 
# Inputs:
#   dir     - The location of the lib directory to generate the process_list to
#   run_dir - The location of the control_loop directory to run the scripts
def check_process(dir,run_dir):
    data = dict()
    #See if there is a file for the config already
    try:
        with open(f"{dir}/process_list.json", "r+") as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()
            logger.info(f"Updating file {dir}/process_list.json")
    #If there isnt a config file create it  
    except Exception as e:
        fh = open(f'{dir}/process_list.json','w+')
        logger.info(f"File {dir}/process_list.json created")
        fh.close()
        subprocess.call(['chmod','0777',dir+'/process_list.json'])
        logger.info(f"Permissions changed on {dir}/process_list.json to 777")
    # Finally write to the file
    finally:
        # Where python is 
        python = '/home/openhabian/Environments/env_1/bin/python3'
        process = ["meter_1_log_data.py","meter_2_log_data.py","control_loop_one.py","control_loop_two.py"]
        # Open the file 
        with open(f"{dir}/process_list.json", "w+") as jsonFile:
            for p in process:
                # Check if the process is in the JSON file 
                if p in data:
                    # Process is in JSON file
                    # Check if it is running
                    # This will not kill it as it is a 0 command 
                    try:
                        os.kill(data[p], 0)
                    except OSError:
                        # Process is no longer running, set it running and record PID
                        logger.info(f"Process {p} not running, ID: {data[p]}")
                        cmd = run_dir+p
                        process = subprocess.Popen([python,cmd,"&"])
                        logger.info(f"Process {p} now running, process ID: {process.pid}")
                        data[p] = process.pid
                    else:
                        # Process is running, do not change the PID 
                        logger.info(f"Process {p} already running, ID:{data[p]}")                
                else:
                    #Process is not in the JSON file
                    #Start the process and save the PID to the JSON file 
                    logger.info(f"Process {p} is not in procces_list.json")
                    cmd = run_dir+p
                    process = subprocess.Popen([python,cmd,"&"])
                    logger.info(f"Process {p} launched, PID of {process.pid} added to JSON file")
                    data[p] = process.pid
            json.dump(data,jsonFile)



##main##
# The purpose of this function is to query OpenHAB and see what smart plugs are configured 
# If smart plugs are found an entry for them is added to the database 
# Then the information to instantiate a new AeotechZW096 instance in the control loop file
# Is added to the config.json file in the lib directory 
async def main():
    #Crete a database connection
    conn = await MySQL.connect()
    #Intitialse an opeb_HAB object 
    hub = open_HAB()
    #Log the hub data to the "hub" table
    await hub.initialise_hub_data(conn)
    #Get the things configured in open_HAB setup
    await hub.get_things()
    #Sort the items based on brand type (Currently only using AeotechPlug, reading the smartMeter in Python)
    await hub.sort_AeotechZW096()

    #Loop through each of the devices found 
    if hub.AeotechZW096things is not None:
        for key, plug in hub.AeotechZW096things.items():
            # If the plug is offline do not include it in the config file 
            if (plug.status['status']) != "ONLINE":
                logger.warning(f"{plug.UID} is offline not including in config file")
            else:
                #Log to the "Devices" table in community_grid
                await plug.update_devices_data(conn)
                #Log to the "items" table in community_grid
                await plug.update_items_data(conn)
                #Write the configuration file for controlling the scripts
                await plug.write_config(plug.switch['UID'],plug.UID,'/home/openhabian/Environments/env_1/openHAB_Proj/lib')
     

##The script starts execution here##
#Get the event loop
loop = asyncio.get_event_loop()
#Run the main() function 
loop.run_until_complete(main())
dir = '/home/openhabian/Environments/env_1/openHAB_Proj/lib'
run_dir = '/home/openhabian/Environments/env_1/openHAB_Proj/control_loop/'
# Run the check_process function
check_process(dir,run_dir)
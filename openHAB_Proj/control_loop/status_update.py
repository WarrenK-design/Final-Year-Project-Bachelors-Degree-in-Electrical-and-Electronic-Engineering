#!/usr/bin/env python

#Author:    Warren Kavanagh
#Last edit: 09/05/2020

##Description##
# This script is called from an OpenHAB rule 
# When a smart plug in OpenHAB changes state this script will be called
# This script logs the change of state to the database in order to keep track of the devices in the network  

##Modules to Import##
# argparse      - Allows for parsing of command line inputs
# sys       	- Used to add the path to the OpenHAB_Proj directory
# AeotechZW096  - Class for the smart plug instances
# MySQL         - Class for interfacing with SQL database 
# asyncio       - Implements Asynchrounous function calls in Python
# logging       - Sets up log file for this script 
import argparse
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.AeotechZW096 import AeotechZW096
from openHAB_Proj import MySQL
import asyncio
import logging

##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/status_update.log') #Get a file handler
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)

## update_device ##
# The purpose of this function is to update the device table in the SQL database 
# Inputs:
#   plug - An instance of the AeotechZW096 class 
async def update_device(plug):
    try:
        logger.info("Creating connection to database using MySQL.connect() function")
        # Create a connection to the database 
        conn = await MySQL.connect()  
        # Update the status plug in the devices table of the SQL database 
        await plug.update_devices_data(conn)
        logger.info(f"Device {plug.UID} status updated to {plug.status['status']} in community_grid database table Devices")
    except Exception as e:
        logger.exception("Could not update entry {plug.UID} in device table of community_grid database")
    finally:
        # Close the connection to the database 
        conn.close()
        await plug.session.close()

# Parse the arguments to the script 
# The input to this script is the UID of a plug that has changed state 
parser = argparse.ArgumentParser()
parser.add_argument("-u","--UID", help="The UID of the device")
args = parser.parse_args()
# Instatiate an AeotechZW096() instance
plug = AeotechZW096()
# Assign the UID inputted to the instance  
plug.UID = args.UID
# Get an event loop 
loop = asyncio.get_event_loop()
logger.info(f"Entering event loop")
# Pass the update_device() function to the event loop and run 
loop.run_until_complete(update_device(plug))
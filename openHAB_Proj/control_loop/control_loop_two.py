#!/usr/bin/env python

#Author:    Warren Kavanagh
#Last edit: 09/05/2020

##Modules to Import##
# sys                  - Used to add the path of the openHAB Package
# smart_meter          - Class used to read the smart meters currently configured
# MySQL                - Functions to log data from smart meter to database 
# AsyncModbusTCPClient - Class needed to make Modbus Connection 
# schedulers           - Module used with the AsyncModbusTCPClient to make Async modbus calls
# AeotechZW096         - Class for the smart plugs being used  
# asyncio              - Implement Asynchrounous function calls within Python
# logging              - Sets up a log file for the script
# json                 - Used to read the config.json file
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.smart_meters import smart_meter
from openHAB_Proj import MySQL
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from openHAB_Proj.AeotechZW096 import AeotechZW096
import asyncio
import logging
import json

##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/control_loop_two.log') #Get a file handler
file_handler.setFormatter(formatter)
#file_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.INFO)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)

### main ###
# This function implments the control of the smart plugs assigned to this script 
# The database table meter_values is queried for the most up to date meter reading
# The return will be be values for voltage, current, power, reactive_power, apparent_power, power_factor
# Based upon any of these values the plugs can be turned on/off 
# The current implmentation is if the value of voltage is:
# Above 230V then turn on
# Below 225V then turn off  
# Inputs:
#   meter  - The IP address of the smart meter 
#   things - A dictionary containing instances of the AeotechZW096 class this script controls
async def main(meter,things):
        logger.info("Executing control loop two event loop")
        while True:
            # Create a connection to the database if one does not exist
            if 'conn' not in locals():
                logger.info("Creating connection to database using MySQL.connect() function")
                conn = await MySQL.connect()  
            logger.info("Querying database using smart_meter.query_all_values")
            
            # Query the meter_values table in the community_grid database for meter 192.168.0.80
            voltage, current, power, reactive_power, apparent_power, power_factor = await MySQL.query_all_values(conn,meter.IP)
            logger.info(f"Query Returned {voltage, current, power, reactive_power, apparent_power, power_factor}")
            # Iterate through the smart plugs in the things dictinary
            for plug_ID, plug in things.items():
                logger.info("Testing plugs based on values from the database")
                # Get the most recent value for the plug state 
                await plug.read_switch()
                await plug.read_status()

                # Ensure that the plug is online 
                if plug.status['status'] == 'OFFLINE':
                    logger.error(f"Plug {plug_ID} is offline and cannot be communicated with")
                    continue
                #Plug is online and communicating 
                else:
                    logger.info(f"Plug {plug_ID} is online")
                
                # If voltage is above 230V then turn on 
                if voltage>230:
                    logger.info(f"Voltage greater than  or equal to 230V, value of {voltage} V turning plug {plug_ID} on")
                    # If the plug is already on then dont send another request 
                    if plug.switch['value'] ==1:
                        logger.info(f"Plug {plug_ID} already on, state unchanged")
                    # If plug is off then send a command to turn on 
                    else:
                        await plug.turn_on()
                        logger.info(f"Command sent to turn {plug_ID} ON")
                 # Volatge is below or equal to 225 V then turn off
                elif voltage<=225:
                    logger.info(f"Voltage less than or equal to 225V, value of {voltage} V turning plug {plug_ID} off")
                    # If plug is on then turn off 
                    if plug.switch['value'] ==1:
                        await plug.turn_off()
                        logger.info(f"Command sent to turn plug {plug_ID} OFF")
                    # If plug is already off then dont change
                    else:
                        logger.info(f"Plug {plug_ID} already OFF, state unchanged")
                # Do not change the state of the plug
                else:
                    logger.info(f"Voltage value of {voltage}, state unchanged, current state of {plug_ID}: {plug.switch['value']}") 

## Meter this script is controlled by ##
meter_2_IP = '192.168.0.80'           
#Node 4 and Node 5
group = "control_loop_two"
## First parse the config file 
with open('/home/openhabian/Environments/env_1/openHAB_Proj/lib/config.json') as json_file:
    data = json.load(json_file)
    #Only insterested in what this script controls 
    #Decided upon by the OpenHAB group 
    try:
        data_1 = data[group]
    except KeyError:
        logger.error(f"No items found for {group}")
    things = dict()
    #Iterate through the Things assigned to this script 
    for key, val in data_1.items():
        plug = AeotechZW096()
        # Give the instance the variables obtained from config.json
        plug.__dict__ = val
        # Things is a dictionary where the key is the plug UID 
        # The value is an instnace of the Aeotech class
        things[plug.UID] = plug

# Get the event loop   
loop = asyncio.get_event_loop()
# Create an instance of AsyncModbusTCPClient which is connected to meter 192.168.0.80
loop, client = ModbusClient(schedulers.ASYNC_IO,host =meter_2_IP, loop=loop)
logger.info(f"Creating smart meter instance with IP of {meter_2_IP}")
# Create an instance of the smart_meter class passing the IP and connection to meter 192.168.0.80
meter_2 = smart_meter(meter_2_IP,client)
# Add main() to the event loop as a task passing smart_meter instance and dictionary of AeotechZW096 instances
loop.create_task(main(meter_2,things))
logger.info(f"Entering event loop")
# Run the loop forever 
loop.run_forever()




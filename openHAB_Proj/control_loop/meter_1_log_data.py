#!/usr/bin/env python

#Author:    Warren Kavanagh 
#Last edit: 08/05/2020

##Modules to Import##
# sys                  - Used to add the path of the openHAB Package
# smart_meter          - Class used to read the smart meters currently configured
# MySQL                - Functions to log data from smart meter to database 
# AsyncModbusTCPClient - Class needed to make Modbus Connection 
# schedulers           - Module used with the AsyncModbusTCPClient to make Async modbus calls
# asyncio              - Implement Asynchrounous function calls within Python
# JSON                 - Used to read the config.json file
# logging              - Sets up a log file for the script 
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.smart_meters import smart_meter
from openHAB_Proj import MySQL
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
import asyncio
import logging


##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/meter_1_log_data.log') #Get a file handler
file_handler.setFormatter(formatter)
#file_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.INFO)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)

###main###
# Used to log data to the database from meter 192.168.0.116
# Inputs:
#   meter - Instance of the smart_meter class with a connection to the meter 192.168.0.116
async def main(meter):
        logger.info("Executing meter_1 event loop")
        while True:
            # Create a connection to the database if there is not already one 
            if 'conn' not in locals():
                logger.info("Creating connection to database using MySQL.connect() function")
                conn = await MySQL.connect()  
            logger.info(f"Calling function read_all() from smart_meter class for meter {meter.IP}")
            # Read the meters values and submit the results to the database 
            await meter.read_all(conn)

## IP Address of the meter this script logs data from ##
meter_1_IP = '192.168.0.116'
# Get the event loop 
loop = asyncio.get_event_loop()
# Create an instance of AsyncModbusTCPClient which is connected to meter 192.168.0.116
loop, client = ModbusClient(schedulers.ASYNC_IO,host =meter_1_IP, loop=loop)
logger.info(f"Creating smart_meter instance for {meter_1_IP}")
# Create an instance of the smart_meter class passing the IP and connection to meter 192.168.0.116
meter_1 = smart_meter(meter_1_IP,client)
# Add the task main() to the event loop 
loop.create_task(main(meter_1))
# Run the event loop forever 
loop.run_forever()




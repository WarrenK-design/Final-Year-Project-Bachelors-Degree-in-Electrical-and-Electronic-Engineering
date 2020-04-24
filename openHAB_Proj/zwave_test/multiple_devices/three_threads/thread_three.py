#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 01/04/2020

##Description##
#The function of this script is to control smart devices based off meter_1. readings
#The devices that will be controlled by this script are located in the file lib/config.json under Meter_1
#The values in this config file will be used to instatiate objects 
#The JSON data is orgainsed as follows:
#{
# SCRIPT_1:{
#             THING_1:{
#                       INSTATIATION_INFO
#           }  
# 
#SCRIPT_2:{
#             THING_2:{
#                       INSTANTIATION_INFO
#                      }  
#         }
#
#}

##Modules to Import##
# sys               - Used to add the path of the openHAB Package
# smart_meter       - Class used to read the smart meters currently configured
# JSON              - Used to read the config.json file
# AeotechZW096      - Class for the smart plugs being used   
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.smart_meters import smart_meter
from openHAB_Proj.AeotechZW096 import AeotechZW096
from openHAB_Proj import MySQL
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
import asyncio
import json
import logging 
import os
import sys
import csv


##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/meter_1.log') #Get a file handler
file_handler.setFormatter(formatter)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)
#os.chmod('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/meter_1.log', 0o777)

async def main(things):
    file_name = "results/thread_three_results"
    with open(file_name, mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print("Executing thread_1 event loop")
        while True:
            for plug in things:
                await plug.read_voltage(csv_writer)
               
               
               
               # if (plug.switch['value']) == 0:
               #     print("OFF")
               #     await plug.turn_on()
               # else:
               #     print("ON")
               #     await plug.turn_off()
               # await plug.turn_on()
          #  if 'conn' not in locals():
          #      logger.info("Creating connection to database using MySQL.connect() function")
          #      conn = await MySQL.connect()  
          #  logger.info("Attempting to read voltage using smart_meter.read_voltage()")
          #  await meter.read_voltage(conn)
         #   logger.info("Attempting to read power using smart_meter.read_kw()")
          #  await meter.read_kw(conn)
          #  logger.info("Attempting to read current using smart_meter.read_current()")
          #  await meter.read_current(conn)
          #  volts, power, current = await MySQL.queryVCP(conn,csv_writer)



group = "test"
## First parse the config file 
with open('/home/openhabian/Environments/env_1/openHAB_Proj/lib/config.json') as json_file:
    data = json.load(json_file)
    #Only insterested in what this script controls 
    try:
        data_1 = data[group]
    except KeyError:
        logger.exception("meter_1.py will not be executed, no configuration for 'meter_1' in config.json\nTracback Error shown below")
        sys.exit()
    things = list()
    #Iterate through the Things assigned to this script 
    for key, val in data_1.items():
        plug = AeotechZW096()
        plug.__dict__ = val
        things.append(plug)
loop = asyncio.get_event_loop()
#loop, client = ModbusClient(schedulers.ASYNC_IO,host ="192.168.0.116", loop=loop)
#meter_1 = smart_meter('192.168.0.116',client)
loop.create_task(main(things))
loop.run_forever()

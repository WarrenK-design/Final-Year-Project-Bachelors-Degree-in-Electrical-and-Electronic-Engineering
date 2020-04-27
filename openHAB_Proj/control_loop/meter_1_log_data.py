#!/usr/bin/env python

##Modules to Import##
# sys               - Used to add the path of the openHAB Package
# smart_meter       - Class used to read the smart meters currently configured
# JSON              - Used to read the config.json file
# AeotechZW096      - Class for the smart plugs being used   
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.smart_meters import smart_meter
from openHAB_Proj import MySQL
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
import asyncio
import csv
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
file_handler.setLevel(logging.WARNING)
#subprocess.call(['chmod','0777','/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/config.log'])
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)
#os.chmod('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/config.log', 0o777)

meter_1_IP = '192.168.0.116'
async def main(meter):
        print("Executing meter_1 event loop")
        while True:
            if 'conn' not in locals():
                logger.info("Creating connection to database using MySQL.connect() function")
                conn = await MySQL.connect()  
            logger.info(f"Calling function read_all() from smart_meter class for meter {meter.IP}")
            await meter.read_all(conn)


loop = asyncio.get_event_loop()
loop, client = ModbusClient(schedulers.ASYNC_IO,host =meter_1_IP, loop=loop)
logger.info(f"Creating smart_meter instance for {meter_1_IP}")
meter_1 = smart_meter(meter_1_IP,client)
loop.create_task(main(meter_1))
loop.run_forever()




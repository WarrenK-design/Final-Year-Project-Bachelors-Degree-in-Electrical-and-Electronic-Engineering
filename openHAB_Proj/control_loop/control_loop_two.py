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
from openHAB_Proj.AeotechZW096 import AeotechZW096
import asyncio
import csv
import logging
import json
from datetime import datetime


##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/control_loop_two.log') #Get a file handler
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

meter_2_IP = '192.168.0.80'
async def main(meter,things):
        logger.info("Executing control loop two event loop")
        with open('/home/openhabian/Environments/env_1/openHAB_Proj/control_loop/results/control_loop_2.csv', mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while True:
                if 'conn' not in locals():
                    logger.info("Creating connection to database using MySQL.connect() function")
                    conn = await MySQL.connect()  
                logger.info("Querying database using smart_meter.query_all_values")
                #await mysql.query_all_values(conn,meter.ip,csv_writer)
                voltage, current, power, reactive_power, apparent_power, power_factor = await MySQL.query_all_values(conn,meter.IP)
                logger.info(f"Query Returned {voltage, current, power, reactive_power, apparent_power, power_factor}")
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
                        logger.info(f"Voltage greater than 230V, value of {voltage} V turning plug {plug_ID} on")
                        # If the plug is already on then dont send another request 
                        if plug.switch['value'] ==1:
                            logger.info(f"Plug {plug_ID} already on, state unchanged")
                        # If plug is off then send a command to turn on 
                        else:
                            await plug.turn_on()
                            csv_writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],plug_ID,"ON",voltage])
                            logger.info(f"Command sent to turn {plug_ID} ON")
                    # Volatge is below 230 V then turn off
                    else:
                        logger.info(f"Voltage less than 230V, value of {voltage} V turning plug {plug_ID} off")
                        # If plug is on then turn off 
                        if plug.switch['value'] ==1:
                            await plug.turn_off()
                            csv_writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],plug_ID,"OFF",voltage])
                            logger.info(f"Command sent to turn plug {plug_ID} OFF")
                        # If plug is already off then dont change
                        else:
                            logger.info(f"Plug {plug_ID} already OFF, state unchanged")
               
#Node 4 and Node 5
group = "control_loop_two"
## First parse the config file 
with open('/home/openhabian/Environments/env_1/openHAB_Proj/lib/config.json') as json_file:
    data = json.load(json_file)
    #Only insterested in what this script controls 
    try:
        data_1 = data[group]
    except KeyError:
        logger.error(f"No items found for {group}")
        sys.exit()
    things = dict()
    #Iterate through the Things assigned to this script 
    for key, val in data_1.items():
        plug = AeotechZW096()
        plug.__dict__ = val
        # Things is a dictionary where the key is the plug UID 
        # The value is an instnace of the Aeotech class
        things[plug.UID] = plug
    
loop = asyncio.get_event_loop()
loop, client = ModbusClient(schedulers.ASYNC_IO,host =meter_2_IP, loop=loop)
logger.info(f"Creating smart meter instance with IP of {meter_2_IP}")
meter_2 = smart_meter(meter_2_IP,client)
loop.create_task(main(meter_2,things))
logger.info(f"Entering event loop")
loop.run_forever()




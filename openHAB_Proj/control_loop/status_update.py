#!/usr/bin/env python

# The input to the script will be the UID of the device
# Need to take this UID and update the devic 
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
#subprocess.call(['chmod','0777','/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/config.log'])
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)
#os.chmod('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/config.log', 0o777)

async def update_device(plug):
    try:
        logger.info("Creating connection to database using MySQL.connect() function")
        conn = await MySQL.connect()  
        await plug.update_devices_data(conn)
        logger.info(f"Device {plug.UID} status updated to {plug.status['status']} in community_grid database table Devices")
        print(f"Device {plug.UID} status updated to {plug.status['status']} in communty_grid database table Devices")
    except Exception as e:
        logger.exception("Could not update entry {plug.UID} in device table of community_grid database")
    finally:
        conn.close()
        await plug.session.close()

parser = argparse.ArgumentParser()
parser.add_argument("-u","--UID", help="The UID of the device")
args = parser.parse_args()
plug = AeotechZW096()
plug.UID = args.UID
loop = asyncio.get_event_loop()
logger.info(f"Entering event loop")
loop.run_until_complete(update_device(plug))
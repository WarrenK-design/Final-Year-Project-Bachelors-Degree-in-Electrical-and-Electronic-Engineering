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

meter_2_IP = '192.168.0.80'
async def main(meter):
        print("Executing meter_2 event loop")
        with open('results/meter_2.csv', mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while True:
                if 'conn' not in locals():
                    print("Creating connection to database using MySQL.connect() function")
                    conn = await MySQL.connect()  
                await MySQL.query_all_values(conn,meter.IP,csv_writer)


loop = asyncio.get_event_loop()
loop, client = ModbusClient(schedulers.ASYNC_IO,host =meter_2_IP, loop=loop)
meter_2 = smart_meter(meter_2_IP,client)
loop.create_task(main(meter_2))
loop.run_forever()




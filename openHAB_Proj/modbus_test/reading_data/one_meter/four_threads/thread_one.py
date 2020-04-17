#!/usr/bin/env python
##Modules to Import##
# sys               - Used to add the path of the openHAB Package
# smart_meter       - Class used to read the smart meters currently configured
# JSON              - Used to read the config.json file
# AeotechZW096      - Class for the smart plugs being used   
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.smart_meters import smart_meter
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import asyncio
import logging 
import csv

# IP address of the smart meter 
meter_IP = "192.168.0.116"

async def main(meter):
    file_name = "results/thread_one_result.csv"
    with open(file_name, mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print("Executing thread one event loop")
        while True:
            await meter.read_all(csv_writer)

loop = asyncio.get_event_loop()
loop, client = ModbusClient(schedulers.ASYNC_IO,host =meter_IP, loop=loop)
meter = smart_meter(meter_IP,client)
loop.create_task(main(meter))
loop.run_forever()
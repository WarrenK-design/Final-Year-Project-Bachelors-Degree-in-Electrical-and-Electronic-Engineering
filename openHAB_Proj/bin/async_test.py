#!/usr/bin/env python
import asyncio
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from datetime import datetime
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj import MySQL
from openHAB_Proj.open_HAB import open_HAB
from openHAB_Proj.smart_meters import smart_meter

#async def main():
#    ##The process##
#    #Intitialse an opeb_HAB object 
#    obj = open_HAB()
#    #get a database connection 
#    conn = await MySQL.connect()
#    #Log the hub data to the "hub" table
#    await obj.initialise_hub_data(conn)
#    #Get the things configured in open_HAB setup
#    await obj.get_things()
#    await obj.sort_AeotechZW096()
#    ##Close the http session 
#    #Loop through each of the devices found 
#    if obj.AeotechZW096things is not None:
#        for key, plug in obj.AeotechZW096things.items():
#            if (plug.status['status']) != "ONLINE":
#                print(f"{plug.UID} is offline not including in config file")
#            else:
#   #            print(f"{plug.UID} is online")
#                await plug.update_devices_data(conn)
#                await plug.update_items_data(conn)
#    await obj.session.close()

async def main(meter):
    conn = await MySQL.connect()
    #val = "230"
    #IP = "298"
    #await MySQL.update_voltage(val,IP,conn)
    #await open_HAB.session.close()
    #print(help(ModbusClient))
    #a = smart_meter('192.168.0.116',loop) 
    print("In loop")
    await meter.read_voltage(conn)
    #print(a)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start = datetime.now()
    print(start)
    ##The process##
    #Intitialse an opeb_HAB object 
    #obj = open_HAB()
    #Log the hub data to the "hub" table
    #obj.initialise_hub_data()
    #Get the things configured in open_HAB setup
    #obj.get_things()
    #Sort the items based on brand type (Currently only using AeotechPlug, reading the smartMeter in Python)
    #obj.sort_AeotechZW096()
    #Intitialse an opeb_HAB object 
    loop, client = ModbusClient(schedulers.ASYNC_IO,host ="192.168.0.116", loop=loop)
    #print(client)
    meter = smart_meter('192.168.0.116',client)
    loop.run_until_complete(main(meter))
    end = datetime.now()
    print(datetime.now()-start)
    print(end)
#!/usr/bin/env python

#The purpose of this test is turn the four devices on and off with a delay in each loop 
#You can turn a group of switches on/off if all the switches belong to the same "Group" in openHAB
#This test assumes that all the plugs belong to the openHAB group "test_on_off"

import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
#from openHAB_Proj.AeotechZW096 import AeotechZW096
from openHAB_Proj.open_HAB import open_HAB
import asyncio
import json
import os
import sys
import csv
import time



async def main(hub,group,delay):
    print("Executing four_devices event loop")
    while True:
        time.sleep(delay)
        if (await hub.read_item(group)) == "ON":
            print("Turn OFF")
            await hub.item_off(group)
        elif(await hub.read_item(group)) == "OFF":
            print("Turn ON")
            await hub.item_on(group)

delay = 0.1
group = "test_on_off"
hub = open_HAB()
loop = asyncio.get_event_loop()
loop.create_task(main(hub,group,delay))
loop.run_forever()

#!/usr/bin/env python

#The purpose of this test is turn the four devices on and off as quick as possible 

import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.smart_meters import smart_meter
from openHAB_Proj.AeotechZW096 import AeotechZW096
import asyncio
import json
import os
import sys
import csv



async def main(things):
        print("Executing four_devices event loop")
        while True:
            for plug in things:
                await plug.update_all()
                if (plug.switch['value']) == 0:
                    await plug.turn_on()
                else:
                    await plug.turn_off()


group = "test"
## First parse the config file 
with open('/home/openhabian/Environments/env_1/openHAB_Proj/lib/config.json') as json_file:
    data = json.load(json_file)
    #Only insterested in what this script controls 
    try:
        data_1 = data[group]
    except KeyError:
        print("No groups found")
        sys.exit()
    things = list()
    #Iterate through the Things assigned to this script 
    for key, val in data_1.items():
        plug = AeotechZW096()
        plug.__dict__ = val
        things.append(plug)

loop = asyncio.get_event_loop()
loop.create_task(main(things))
loop.run_forever()

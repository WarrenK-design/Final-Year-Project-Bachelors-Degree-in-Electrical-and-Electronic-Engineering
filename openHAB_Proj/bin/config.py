#!/usr/bin/env python
#This script will contain the continous loop that will 
#Run to check the current values of the meters 
#And then write these values to the 

## Modules to import ##
# sys          - Used to navigate directorys in python 
# open_HAB     - Contains the open_HAB Class with functions for interfacing with openHAB
# smart_meters - Contains functions for interfacing with modubus meters 
# datetime     - Used for getting time in python 
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.open_HAB import open_HAB
from openHAB_Proj import smart_meters
from datetime import datetime
import pprint
import os

#1. Retrieve all things and items in configuration
#2. Sort the items based upon type/name 
#   z-wave items 
#   modbus TCP items 
#3. Multithread this process so it is operating at seprate times 

##Step One: Retrieve the items## 
obj = open_HAB()
obj.initialise_hub_data()
obj.get_things()
##Step Two: Sort the items based on brand type##
obj.sort_AeotechZW096()
 ##Step Three: Control Loop##
for key, plug in obj.AeotechZW096things.items():
    plug.write_config(plug.items,plug.UID,'/home/openhabian/Environments/env_1/openHAB_Proj/lib')
print(f"Start Up Script Executed")
#!/usr/bin/env python
#This script will contain the continous loop that will 
#Run to check the current values of the meters 
#And then write these values to the 
import sys
sys.path.append(r'/home/openhabian/Environments/env_1/openHAB_Proj/')
from openHAB_Proj.open_HAB import open_HAB
import time 


if __name__ == '__main__':
    #1. Retrieve all things and items in configuration
    #2. Sort the items based upon type/name 
    #   z-wave items 
    #   modbus TCP items 
    #3. Multithread this process so it is operating at seprate times 

    ##Step One: Retrieve the items## 
    obj = open_HAB()
    obj.get_things()

    ##Step Two: Sort the items based on brand type##
    obj.sort_AeotechZW096()

    ##Step Three: Control Loop##
    for key, plug in obj.AeotechZW096things.items():
        #val.update_all()
        print('********************************')
        plug.read_status()
        plug.turn_on()
        plug.read_switch()
        time.sleep(5)
        plug.turn_off()
        plug.read_switch()
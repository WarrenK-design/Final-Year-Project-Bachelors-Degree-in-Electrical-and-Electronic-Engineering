#!/usr/bin/env python
#This script will contain the continous loop that will 
#Run to check the current values of the meters 
#And then write these values to the 
import sys
import time 
sys.path.append(r'..')


from openHAB_Proj.open_HAB import open_HAB


if __name__ == '__main__':
    obj = open_HAB()
    obj.get_items()
    print(obj.read_items())
    print(obj.get_switches())
    while True:
        for key, value in obj.switches.items():
            if (obj.read_item(value)=="OFF"): 
                obj.item_on(value)
            else:
                obj.item_off(value)
            time.sleep(2)
    




#while True:
    #    print(obj.read_items(),datetime.datetime.now() )
#    for key, value in obj.items.items():
#        a = obj.read_items(obj.items[key])
#        print(a)
#    #obj.read_items()
    #print((items.keys()))

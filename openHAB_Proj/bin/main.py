#!/usr/bin/env python
#This script will contain the continous loop that will 
#Run to check the current values of the meters 
#And then write these values to the 
import sys
import datetime 
sys.path.append(r'../lib')
from openHAB_Proj import openHAB_Proj

if __name__ == '__main__':
    obj = openHAB_Proj()
    obj.get_items()
    while True:
        print(obj.read_items(),datetime.datetime.now() )
#    for key, value in obj.items.items():
#        a = obj.read_items(obj.items[key])
#        print(a)
#    #obj.read_items()
    #print((items.keys()))

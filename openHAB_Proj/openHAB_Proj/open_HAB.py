#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 29/02/2020


##TODOLIST##
#TODO: Need a function to check the status of a given item 
#TODO: Need to check the return codes of the HTTP requests  
#TODO: Delete the pprint import when finished 
#TODO: Update get switches 

#This script will contain all of the openHAB functionalitys 
#Functions to be implmented:
#   1. Retrieving items through the REST API  
#   2. Turing items on and off 
#   3. Reading the values of items
#   4. Returng Switch items to implment control over multiple switches 

##Modules to import##
# requests  - Allows script to make HTTP requests   
import requests
import pprint #**********DELETE****************


###  Class: open_HAB  ###
## Description ##
# Class with functions for interfacing with openHAB
# This class will be the parent class for providing basic operations 
# which are not vendor specfic, for example getting all things in openHAB config
# then sorting these things based on vendors 
#
## Functions ##
#   __init__            - Initialses instance variables 
#   get_things          - Gets the current items configured in openHAB
#   openhab             - htttp get request is performed to return the current items
#   read_item           - Read a single item passed to function
#   item_on             - Change an item state passed to function to 'ON'
#   item_off            - Change an item state passed to function to 'OFF'
#   sort_AeotechZW096   - Will create instance of AeotechZW096 if thing configured in openHAB 
#   check_status        - Checks the status of the thing passed to the function 
#   get_switches        - Returns a dictionary of switch items 
#
## Class Variables ##
#   things  - Stores the JSON data for the config of all things in openHAB 
#
## Instance Variables ##
#   base_url[string]                - The destination for the REST requests 
#   switches[dictionary]            - A dictionary which holds all switch items 
#   AeotechZW096things[dictionary]  - Dictonary which stores AeotechZW096 instances, key= label of thing, value = AeotechZW096 instance 

class open_HAB:

    ##class varaiables##
    things = dict()

    ##__init__##
    # Initialise method called when new instance of the open_HAB
    # is instantiated 
    def __init__ (self):
        self.base_url             = 'http://localhost:8080/rest'
        self.switches             = dict() #DELETE NOT USED
        self.AeotechZW096things   = dict()

    ##get_things##
    # This function will get all avalable things 
    # in the openhab configuration setup 
    # A http get request is performed which will return the configuration 
    # of all things on the openHAB setup in JSON. 
    # The JSON data will be stored in a dictionary class variable
    # "things". The "things" variable will then be sorted to find the type of things
    def get_things(self):
        #Get request, returns a request object 
        res = requests.get(f'{self.base_url}/things')
        #Get the JSON from the request object, store in a class variable "things"
        open_HAB.things = (res.json())
        for thing in open_HAB.things:
            if thing['thingTypeUID'] == "zwave:aeon_zw096_00_000":
                from openHAB_Proj import AeotechZW096 #Only importing as needed resolves "cylic import" https://stackabuse.com/python-circular-imports/
                self.AeotechZW096things[thing['label']] = AeotechZW096.AeotechZW096(thing,thing['UID'])
     
    ##sort_AeotechZW096##
    # This function will sort the AeotechZW096 things found in 
    # the opeHAB configuration and assign values to the AeotechZW096 insance variables
    # stored in the AeotechZW096things dictionary 
    def sort_AeotechZW096(self):
        # Fill the variables with the items associated with a AeotechZW096 switch
        # key is the label given to the thing in openHAB config
        # aeotechobj is an instance of the AeotechZW096 class
        for key, aeotechobj in self.AeotechZW096things.items():
            aeotechobj.sort_vars()


    ##read item##
    # This function will read an item that is passed to it 
    # and return the value that is read
    # Inputs:
    #    item - The name of the item  e.g Voltage_Zwave_Node3
    def read_item(self,item):
        # Get request, returns a request object 
        res = requests.get(f'{self.base_url}/items/{item}/state')
        return res.text
   
    ##item_on##
    # This function will turn the item that is passed to it on 
    # Inputs:
    #    item - The name of the item to turn on
    def item_on(self,item):
        res = requests.post(f'{self.base_url}/items/{item}',data="ON")
        
    ##item_off##
    # This function will turn the item that is passed to it off
    # Inputs:
    #    item - The name of the item to turn off 
    def item_off(self,item):
        res = requests.post(f'{self.base_url}/items/{item}',data="OFF")


    ##check_status##
    # Checks the status of a given thing passed to it
    #  
    # Inputs:
    #   UID - The UID of the thing to check the status of 
    def check_status(self,UID):
        res = requests.get(f'{self.base_url}/things/{UID}/status')
        return (res.json())
                        
    ##get_switches##
    #This function will get all the switch items 
    #It calls the function get_items which populates the class variable items
    #This will then be sorted through to only obtain the switch items and store
    #the switch items in a dictionary 'switches'
    def get_switches(self):
        for key, value in self.items.items():
            if isinstance(value,SwitchItem):
                self.switches[key] = value
        return self.switches

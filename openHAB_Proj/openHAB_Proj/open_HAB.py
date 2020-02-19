#!/usr/bin/env python
#This script will contain all of the openHAB functionalitys 
#Functions to be implmented:
#   1. Retrieving items from a given location 
#   2. Turing items on and off 
#   3. Reading the values of items

##Librarys to import##
#openhab - A package to interface with the openHAB REST API  
from openhab import openHAB
from openhab.items import SwitchItem

###open_HAB###
#Class with functions for interfacing with openHAB
#
#Functions:
#   __init__    - Initialses class variables 
#   get_items   - Gets the current items configured in openHAB
#   openhab     - An object from the class openHAB
#   read_items  - Reads the current values of the items configured
#   read_item   - Read a single item passed to function
#   item_on     - Turn an item state to 'ON'
#   item_off    - Turn an item state to 'OFF'
#   get_switches- Returns a dictionary of switch items 
#
#Class Variables:
#   base_url[string]    - The destination for the REST requests 
#   items[dictionary]   - The items currently configured in openHAB
#   openhab[OpenHAB]    - An openHAB object which establishes connection to API
#   switches[dictionary]- A dictionary which holds all switch items 

class open_HAB:
    def __init__ (self):
        self.base_url = 'http://localhost:8080/rest'
        self.items    = dict() 
        self.openhab  = openHAB(self.base_url)
        self.switches = dict()
 
    ##get_items##
    #Gets the items that are currently setup 
    #Stores them in a class variable 'items' this is a dictionary 
    def get_items(self):
        self.items    = self.openhab.fetch_all_items()
        return self.items
    
    ##read_items#
    #This function will read all items configured in openhab
    #Returns a dictionary where the key is the item name and the value is its state 
    def read_items(self):
        temp_items = dict()
        for key, value in self.items.items():
            temp_items[key] = value.state
        return temp_items
    
    ##read_items##
    #This function will read a single item passed to it 
    #The return is the item state
    #Inputs:
    #   item - An item type of the openHAB class
    def read_item(self,item):
        return item.state

    ##item_on##
    #This function will turn the item that is passed to it on 
    #Inputs:
    #   item - An item type of the openHAB class
    def item_on(self,item):
        item.command('ON')

    ##item_off##
    #This function will turn the item that is passed to it off
    #Inputs:
    #   item - An item type of the openHAB class 
    def item_off(self,item):
        item.command('OFF')
                            
    ##get_switches##
    #This function will get all the switch items 
    #It calls the function get_items which populates the class variable items
    #This will then be sorted through to only obtain the switch items and store
    #the switch items in a dictionary 'switches'
    def get_switches(self):
        self.get_items()
        for key, value in self.items.items():
            if isinstance(value,SwitchItem):
                self.switches[key] = value
        return self.switches



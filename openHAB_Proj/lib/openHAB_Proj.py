#!/usr/bin/env python
#This script will contain all of the openHAB functionalitys 
#Functions to be implmented:
#   1. Retrieving items from a given location 
#   2. Turing items on and off 
#   3. Reading the values of items 
from openhab import openHAB

###openHAB_Proj###
#Class with functions for interfacing with openHAB
#
#Functions:
#   __init__    - Initialses class variables 
#   get_items   - Gets the current items configured in openHAB
#   openhab     - An object from the class openHAB
#   read_items  - Reads the current values of the items configured 
#
#Class Variables:
#   base_url[string]    - The destination for the REST requests 
#   items[dictionary]   - The items currently configured in openHAB

class openHAB_Proj:
    def __init__ (self):
        self.base_url = 'http://localhost:8080/rest'
        self.items    = dict() 
        self.openhab  = openHAB(self.base_url)
 
    ##get_items##
    #Gets the items that are currently setup 
    #Stores them in a class variable 'items' this is a dictionary 
    def get_items(self):
        self.items    = self.openhab.fetch_all_items()
    
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


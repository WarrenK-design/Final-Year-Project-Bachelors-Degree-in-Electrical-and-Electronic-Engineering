#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 29/02/2020

##TODOLIST##
#TODO:Delete the pprint import when finished 

##Modules to import##
# open_HAB  - Module which contains the class open_HAB which AeotechZW096 inherits from
from openHAB_Proj import open_HAB
from openHAB_Proj import MySQL
from datetime import datetime
import pprint


###  Class: AeotechZW096  ###
## Description ##
# The purpose of this class is to access AeotechZW096 things configured in openHAB
# directly. Every AeotechZW096 smart plug configured will be an instance of this class.
# Associated with this instance will be attributes unique to the AeotechZW096 model
#
## Base Class ##
# Class name: open_hab
# File      : open_hab.py
# Module    : open_hab
# Package   : openHAB_Proj
# 
## Functions ##
#   __init__            - Initialise instance variables and call base class __init__
#   sort_vars           - Will asses what items are configured for the given AeotechZW096 smart plug 
#   sort_type           - Will assign unique values to inst variables based config found using sort_vars
#   read_voltage        - Read the value of voltage for the given smart plug 
#   read_current        - Read the value of current for the given smart plug 
#   read_switch         - Read the value of the switch for the given smart plug 
#   read_power          - Read the value of power for the given smart plug 
#   read_energy         - Read the value of energy for the given smart plug 
#   update_all          - Update the value of all items associated wth the given smart plug 
#   turn_on             - Turn the given smart plug on          
#   turn_off            - Turn the given smart plug off
#   read_status         - Gets the status of the current thing 
#   update_items_data   - Logs the item values to the items table of the commmunity grid database 
#   update_devices_data - Logs the device values to the device table of the community grid database
#
## Class Variables ##
#   things  - Stores the JSON data for the config of all things in openHAB (Defined in base class) 
#
## Instance Variables ##
# Note each instance will also have the base class open_HAB instance variables
#   config  [dictionary] - The JSON data from openHAB associated with the smart plugs configuration 
#   UID     [string]     - Unique ID assigned to the thing 
#   status  [dictionary] - Stores information on the status of the thing
#   items   [dictionary] - Stores references to the variables which contain the item information  
#   keys    [list]       - The keys which will be used to instatiate dictionarys based on items instatiated 
#These dictionarys are instatiated based on openHAB setup and if configured a reference will be stored in the items dictionary:
#   switch  [dictionary] - Stores information associated with the switch item   
#   voltage [dictionary] - Stores information associated with the voltage item
#   power   [dictionary] - Stores information associated with the power item
#   current [dictionary] - Stores information associated with the current item
#   energy  [dictionary] - Stores information associated with the energy item

class AeotechZW096(open_HAB.open_HAB):

    ##__init__##
    #Initialise method called when new instance of the AeotechZW096
    #is instantiated. The base class open_HAB __init__ method is also called
    #The inputs of config and UID are required if the sorting fuctions are being used 
    #Inputs:
    #   config - The JSON data that describes the smart plug config
    #   UID    - The unique ID assigned to the smart plug 
    def __init__ (self,config=None,UID=None):
        super().__init__()
        self.config                 = config
        self.UID                    = UID
        self.status                 = dict.fromkeys(['status','statusDetail','description']) 
        self.keys    	            = ['name','item','unit','value']
        self.items                  = dict() 


    ##sort_vars##
    #This function sorts the variables of the AeotechZW096 class
    #The JSON data which was found to be associated with the AeotechZW096 things
    #and stored in the "config" variable is parsed with the item names and channel names configured in openHAB
    #beng assigned to instance variables in python 
    def sort_vars(self):
        #First check the status of the thing 
        self.read_status()
        #If the thing is OFFLINE then dont continue setting up variables as they wont have values
        if self.status['status'] !='ONLINE' or self.status['statusDetail'] == 'COMMUNICATION_ERROR':
            print("Device",self.UID,"is offline")
        #Else the thing is ONLINE
        else:
            #json in this loop will be the json data describing
            #each of the channels associated with the given thing
            # linked items is a temporary list to check for index error 
            # If there is an index error then no items are configured  
            linked_items = list()
            for json in self.config['channels']:
                # Try to index the linkeditems list
                try:
                    linked_items = (json['linkedItems'][0])
                # If there is index error set linked_items to null
                except IndexError:
                    linked_items = "Null"
                if json['channelTypeUID'] == 'zwave:switch_binary':
                    self.switch = dict.fromkeys(self.keys)
                    self.sort_type(self.switch,json['channelTypeUID'],linked_items,"Bool")
                    self.items['switch'] = self.switch
                elif json['channelTypeUID'] == 'zwave:meter_kwh':
                    self.energy = dict.fromkeys(self.keys)
                    self.sort_type(self.energy,json['channelTypeUID'],linked_items,"kWh")
                    self.items['energy'] = self.energy
                elif json['channelTypeUID'] == 'zwave:meter_current':
                    self.current = dict.fromkeys(self.keys)
                    self.sort_type(self.current,json['channelTypeUID'],linked_items,"Amps")
                    self.items['current'] = self.current
                elif json['channelTypeUID'] == 'zwave:meter_voltage':
                    self.voltage = dict.fromkeys(self.keys)
                    self.sort_type(self.voltage,json['channelTypeUID'],linked_items,"Volts")
                    self.items['voltage'] = self.voltage
                elif json['channelTypeUID'] == 'zwave:meter_watts':
                    self.power = dict.fromkeys(self.keys)
                    self.sort_type(self.power,json['channelTypeUID'],linked_items,"Watts")
                    self.items['power'] = self.power

    ##sort_type##
    # Gives values to instance variable based on sort_vars function
    # Inputs:
    #   var     - The instance variable to assign a value too 
    #   name    - The value that the name key will point to e.g 'zwave:switch_binary'
    #   item    - The value that the item key will point too e.g 'Switch_Zwave_Node3'
    #   unit    - The units of the given variable e.g Volts 
    def sort_type(self,var,name,item,unit):
        var['name'] = name
        var['item'] = item
        var['unit'] = unit

    ##read_voltage##
    #Reads the voltage of the z-wave node 
    def read_voltage(self):
        if self.status['status']=="OFFLINE":
            self.voltage['value'] = None
        #The return of read_item will be the voltage value 
        else: 
            val = self.read_item(self.voltage['item'])
            if val =='NULL':
                self.voltage['value'] = None    
            else:
                self.voltage['value'] = val
            
    ##read_current##
    #Reads the current of the z-wave node 
    def read_current(self):
        if self.status['status']=="OFFLINE":
            self.current['value'] = None
        #The return of read_item will be the current value 
        else:
            val = self.read_item(self.current['item'])
            if val =='NULL':
                self.current['value'] = None
            else:
                self.current['value'] = val
    
    ##read_switch##
    #Reads the switch of the z-wave node 
    def read_switch(self):
        if self.status['status']=="OFFLINE":
            self.switch['value'] = None
        else:
            #The return of read_item will be the On/Off value 
            val = self.read_item(self.switch['item'])
            if val =='OFF':
                self.switch['value'] = 0
            elif val == 'ON':
                self.switch['value'] = 1
            else:
                self.switch['value'] = None

    ##read_power##
    #Reads the power of the z-wave node 
    def read_power(self):
        if self.status['status']=="OFFLINE":
            self.power['value'] = None
        else:
       	    #The return of read_item will be the watts value 
       	    val = self.read_item(self.power['item'])
       	    if val =='NULL':
       	        self.power['value']= None
       	    else:
       	        self.power['value'] = val
       	    #pprint.pprint(self.power)

    ##read_energy##
    #Reads the switch of the z-wave node 
    def read_energy(self):
        if self.status['status']=="OFFLINE":
            self.energy['value'] = None
        else:
            #The return of read_item will be the kWh value 
            val = self.read_item(self.energy['item'])
            if val =='NULL':
                self.energy['value'] = None
            else:
                self.energy['value'] = val
       #     pprint.pprint(self.energy)

    ##update_all##
    #This function updates all item values for the given node 
    def update_all(self):
        if 'voltage' in self.items:
            self.read_voltage()
        if 'current' in self.items:
            self.read_current()
        if 'switch' in self.items:
            self.read_switch()
        if 'power' in self.items:
            self.read_power()
        if 'energy' in self.items:
            self.read_energy()

    ##turn_off##
    #Turns the smart plug on 
    def turn_on(self):
        if self.status['status'] == 'OFFLINE':
            pass
        else:
            #Call the item_on method from the base class
            self.item_on(self.switch['item'])

    ##turn_off##
    #Turns the smart plug off 
    def turn_off(self):
        if self.status['status'] == 'OFFLINE':
            pass
        else:
            #Call the item_off method from the base class
            self.item_off(self.switch['item'])

    ##read_status##
    #Reads the status of the smart plug
    def read_status(self):
        #Call the check_status in the base class
        desc = (self.check_status(self.UID))
        self.status['status'], self.status['statusDetail'] = desc['status'], desc['statusDetail']
        if 'description' in desc:
            self.status['description'] = desc['description']

    ##update_items_data##
    #Function will update the items table in the community_grid database
    def update_items_data(self):
        # sql_data will store a list of tuples which contain infomation to be written to the items table
        sql_data = list()
        #Update the values first to most up to date values
        self.update_all()
        #Iterate through the avaialable items
        for key, val in self.items.items():
            sql_data.append((val['item'],self.UID,val['value'],val['unit'],datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        #Pass these to the update_item function of MySQL
        MySQL.insert_item(sql_data)

    ##update_devices_data##
    #Function will call the insert_device function from MySQL passing it the values for the 
    #Aeotech_plug 
    def update_devices_data(self):
        # Update the status first 
        self.read_status()
        #DeviceID               - self.UID
        #RaspberryPi_ID         - self.MAC
        #Status                 - self.status['status']
        #Status_Detail          - self.status['statusDetail']
        #Communication_Protocol - Z-Wave 
        #Binding                - Z-Wave Binding description
        MySQL.insert_device(self.UID,self.MAC,self.status['status'],self.status['statusDetail'],self.status['description'],'Z-Wave','Z-Wave Binding',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    ##update_volts##
    #Function to add an entry to the voltages table 
    #With the information from an Aeotech plug 
    def update_volts(self):
        #Get the most recent value for voltage
        self.read_voltage()
        MySQL.update_voltage(self.voltage['value'],datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 29/02/2020


##TODOLIST##
#TODO: Need a function to check the status of a given item 
#TODO: Need to check the return codes of the HTTP requests  
#TODO: Delete the pprint import when finished 

#This script will contain all of the openHAB functionalitys 
#Functions to be implmented:
#   1. Retrieving items through the REST API  
#   2. Turing items on and off 
#   3. Reading the values of items
#   4. Returng Switch items to implment control over multiple switches 

##Modules to import##
# requests  - Allows script to make HTTP requests  https://requests.readthedocs.io/en/master/
# UUID      - Used to get the MAC address of the raspberry pi  https://docs.python.org/3/library/uuid.html
# re        - Regular expression library for formatting MAC address https://docs.python.org/3/library/re.html 
# MySQL     - The MySQL library to connect to the community grid database
# socket    - Used to get the IP address of the raspberry pi  https://docs.python.org/3/library/socket.html#socket.socket.connect
# datetime  - Used to get the current time for the timestamp 
import requests
import uuid
import re
from openHAB_Proj import MySQL
import socket 
from datetime import datetime
import pprint #**********DELETE****************
import json
import os
import subprocess
import logging 
import asyncio
import aiohttp


##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/open_HAB.log') #Get a file handler
file_handler.setFormatter(formatter)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)
#os.chmod('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/open_HAB.log', 0o777)



###  Class: open_HAB  ###
## Description ##
# Class with functions for interfacing with openHAB
# This class will be the parent class for providing basic operations 
# which are not vendor specfic, for example getting all things in openHAB config
# then sorting these things based on vendors 
#
## Functions ##
#   __init__            - Initialses instance variables 
#   initialise_hub_data - Calls the hub_data function in MySQL mosule to fill in data in table
#   get_things          - Gets the current items configured in openHAB
#   openhab             - htttp get request is performed to return the current items
#   read_item           - Read a single item passed to function
#   item_on             - Change an item state passed to function to 'ON'
#   item_off            - Change an item state passed to function to 'OFF'
#   sort_AeotechZW096   - Will create instance of AeotechZW096 if thing configured in openHAB 
#   check_status        - Checks the status of the thing passed to the function 
#   get_thing           - Gets a single thing based on the thing UID  
#   get_item            - Gets the item configuration 
#   write_config        - Writes the config JSON file for the current item setup 
#
## Class Variables ##
#   things  - Stores the JSON data for the config of all things in openHAB
#   session - A aiohttp session to interface with the rest API  
#
## Instance Variables ##
#   base_url[string]                - The destination for the REST requests 
#   AeotechZW096things[dictionary]  - Dictonary which stores AeotechZW096 instances, key= label of thing, value = AeotechZW096 instance 
#   MAC                             - The MAC address of the RaspberryPi openHAB is running on 
class open_HAB:

    ##class varaiables##
    things = dict()
    session = aiohttp.ClientSession()

    ##__init__##
    # Initialise method called when new instance of the open_HAB
    # is instantiated 
    def __init__ (self):
        logger.info(f"New open_HAB object created {self}")
        self.base_url             = 'http://localhost:8080/rest'
        self.AeotechZW096things   = dict()
        self.MAC                  = ':'.join(re.findall('..', format(uuid.getnode(),'x')))

    ##initialise_hub_data##
    #Passes the required values to the hub_data function in the
    #MySQL module to store information on the hub in the database
    async def initialise_hub_data(self,conn):
        # Get the IP Address of the RaspberryPi
        IP = self.get_IP()
        logger.info(f"IP address for object {self} of: {IP}")
        # Get the current location of the HUB
        await MySQL.hub_data(self.MAC,IP,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),conn)


    ##get_IP##
    # This function gets the IP address of the current hub
    # Its uses the socket library to return the IPV4 address
    # Return:
    #   IP - The IPV4 address of the eth0 interface
    def get_IP(self):
        # Create a socket object using socket.socket
        #   socket.AF_INET - The address family, contained in this family is the IPV4 addrees
        #   socket.SOCK_DGRAM - The socket type
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Make a connection using
        # Address - 8.8.8.8 makes an external connection which resolves full route
        # port    - 80
        try: 
            s.connect(("8.8.8.8", 80))
            logger.info(f"IP address of device found to be: {(s.getsockname()[0])}")
            return(s.getsockname()[0])
        except:
            logger.warning("Could not resolve IP address for hub setting as None")
            return(None)


    ##get_things##
    # This function will get all avalable things 
    # in the openhab configuration setup 
    # A http get request is performed which will return the configuration 
    # of all things on the openHAB setup in JSON. 
    # The JSON data will be stored in a dictionary class variable
    # "things". The "things" variable will then be sorted to find the type of things
    async def get_things(self):
        #Get request, returns a request object 
        logger.info(f"Get request made to {self.base_url}/things")
        async with open_HAB.session.get(f'{self.base_url}/things') as resp:
            res = (await resp.json())
        #Get the JSON from the request object, store in a class variable "things"
        open_HAB.things = res
        for thing in open_HAB.things:
            if thing['thingTypeUID'] == "zwave:aeon_zw096_00_000":
                logger.info(f"Found Aeotech smart plug UID: {thing['UID']}")
                from openHAB_Proj import AeotechZW096 #Only importing as needed resolves "cylic import" https://stackabuse.com/python-circular-imports/
                self.AeotechZW096things[thing['label']] = AeotechZW096.AeotechZW096(thing,thing['UID'])
     
    ##sort_AeotechZW096##
    # This function will sort the AeotechZW096 things found in 
    # the opeHAB configuration and assign values to the AeotechZW096 insance variables
    # stored in the AeotechZW096things dictionary 
    async def sort_AeotechZW096(self):
        if bool(self.AeotechZW096things):
            # Fill the variables with the items associated with a AeotechZW096 switch
            # key is the label given to the thing in openHAB config
            # aeotechobj is an instance of the AeotechZW096 class
            for key, aeotechobj in self.AeotechZW096things.items():
                await aeotechobj.sort_vars()
        else:
            logger.warning("No Aeotech plugs found, the AeotechZW096things is empty")


    ##read item##
    # This function will read an item that is passed to it 
    # and return the value that is read
    # Inputs:
    #    item - The name of the item  e.g Voltage_Zwave_Node3
    #async def read_item(self,item,file):
        # Get request, returns a request object 
    async def read_item(self,item):
        logger.info(f"Get request sent to {self.base_url}/items/{item}/state")
        async with open_HAB.session.get(f'{self.base_url}/items/{item}/state') as resp:
            res = (await resp.text())
            if (resp.status) == 200:
          #      file.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],"OK",self.UID,res])
                return res
            else:
                pass
                #file.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],"FAIL",self.UID,res]) 

   
    ##get_item##
    #Gets the item configuration from openhab
    #Input
    #   item - The name of the item you want to get 
    async def get_item(self,item):
        # Get request, returns a request object
        logger.info(f"Get request sent to {self.base_url}/items/{item}")
        async with open_HAB.session.get(f'{self.base_url}/items/{item}') as resp:
            res = (await resp.json())
        return res


    ##item_on##
    # This function will turn the item that is passed to it on 
    # Inputs:
    #    item - The name of the item to turn on
    async def item_on(self,item):
        logger.info(f"Post request sent to {self.base_url}/items/{item}, data=ON")
        req = f'{self.base_url}/items/{item}'
        async with open_HAB.session.post(url=req,data='ON') as resp:
           rep = (resp.status)  #Need to add check to this
          # if rep == 200:
          #      self.switch["value"] ="ON"

    ##item_off##
    # This function will turn the item that is passed to it off
    # Inputs:
    #    item - The name of the item to turn off 
    async def item_off(self,item):
        logger.info(f"Post request sent to {self.base_url}/items/{item}, data=OFF")
        req = f'{self.base_url}/items/{item}'
        async with open_HAB.session.post(url=req,data='OFF') as resp:
            rep = (resp.status)  #Need to add check to this
#            if rep == 200:
 #               self.switch["value"] ="OFF"

        

    ##check_status##
    # Checks the status of a given thing passed to it
    #  
    # Inputs:
    #   UID - The UID of the thing to check the status of 
    async def check_status(self,UID):
        logger.info(f"Get request sent to {self.base_url}/things/{UID}/status")
        async with open_HAB.session.get(f'{self.base_url}/things/{UID}/status') as resp:
            res = (await resp.json())
        return (res)

    
    ##get_thing##
    #Retrieves the thing based on the UID passed to it 
    #Inputs:
    #   UID - The UID of the thing 
    async def get_thing(self,UID):
        logger.info(f"Get request sent to {self.base_url}/things/{UID}")
        async with open_HAB.session.get(f'{self.base_url}/things/{UID}') as resp:
            res = (await resp.json())
        return res


    ##Write_Config##
    #Writes the config file for the scripts
    #Inputs:
    #   switch - The name of the switch item in openHAB the given script will control 
    #   thing  - A string containing the device UID
    #   dir   - The directory to generate the file to 
    async def write_config(self,switch,thing,dir):
        data = dict()
        res = await (self.get_item(switch))
        
        #See if a group exists first  
        try:
            group = res['groupNames'][0]
            logger.info(f"{switch} found to be part of {group} group in openHAB setup")
        # If a group does not exist then exit the function
        except IndexError:
            logger.warning(f"No group found in openHAB for {switch}, will not be included in config file")
            return 

        #See if there is a file for the config already
        try:
            with open(f"{dir}/config.json", "r+") as jsonFile:
                data = json.load(jsonFile)
                jsonFile.close()
                logger.info(f"Updating file {dir}/config.json")
        
        #If there isnt a config file create it  
        except:
            fh = open(f'{dir}/config.json','w+')
            logger.info(f"File {dir}/config.json created")
            fh.close()
            subprocess.call(['chmod','0777',dir+'/config.json'])
            logger.info(f"Permissions changed on {dir}/config to 777")
        
        # Finally write to the file
        finally:
            # Open the file 
            with open(f"{dir}/config.json", "w+") as jsonFile:
                # Get the group name
                group = res['groupNames'][0]

                #Create a dictionary for it 
                if group not in data:
                    logger.info(f"Entry added for {group} in {dir}/config.json")
                    data[group] = dict()

                #See if there is already an entry for the current thing 
                try:
                    x = data[group][thing]

                #If there is not create a dictionary 
                except KeyError:
                   logger.info(f"New entry created in {dir}/config.json for {thing} under {group}")
                   data[group][thing] = dict()

                # Get the values of each of the variables, will return a string
                obj = json.dumps(self.__dict__)

                #Need to get it in dictinary form to create an object later 
                clone = json.loads(obj)                    
                data[group][thing] = clone

                #Write the entry to the file 
                json.dump(data,jsonFile,indent=4,sort_keys=True)
                jsonFile.close()
                logger.info(f"{dir}/config.json has been updated")
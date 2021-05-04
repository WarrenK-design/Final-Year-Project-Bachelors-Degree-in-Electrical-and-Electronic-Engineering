#!/usr/bin/env python

#Author    - Warren Kavanagh 
#Last edit - 29/02/2020


## Reading a floating point address ##
# The response will contain two registers making a 32 bit floating point number
# Use the BinaryPayloadDecoder.fromRegisters() function to decode
# The coding scheme for a 32 bit float is IEEE 754 https://en.wikipedia.org/wiki/IEEE_754
# The MS Bytes are stored in the first address and the LS bytes are stored in the second address,
# this corresponds to a big endian byte order (Second parameter in function)
# The documentation for the Modbus registers for the smart meter on page 24 says that
# the low word is the first priority, this correspond to a little endian word order (Third parameter in function)


## Modules to Import ##
#ModbusTcpClient      - Modbus Libray to connect to meter 
#Endian               - Used for the coding type of the 32 bit float register
#BinaryPayloadDecoder - Used in the decoding of the 32 bit float registers 
#MySQL                - The MySQL module to connect to the datbase 
#logging          - Module used to log to the log file for this file
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from openHAB_Proj import MySQL
from datetime import datetime
import logging 

##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s')#Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/smart_meters.log')#Get a file handler
file_handler.setFormatter(formatter)
#file_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.INFO)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)



class smart_meter():

    ## __init__ ##
    # Initialiase method to intatiated object 
    # Inputs:
    #   IP - The IP address of the smart meter 
    #   client - A modbus client of type 'pymodbus.client.asynchronous.asyncio.ReconnectingAsyncioModbusTcpClient'
    def __init__(self,IP,client):
        #Create the client object passing the IP address of the subordinate to it 
        logger.info(f"New instance of smart_meter instantaited with IP of {IP}")
        self.IP = IP
        #self.client - 'pymodbus.client.asynchronous.asyncio.ModbusClientProtocol' 
        self.client = client.protocol

    ## read_all_registers ##
    # Reads the registers:
    # V_2 - 0x1112
    # I_2 - 0x1114
    # kW_2 - 0x1116
    # kvar_2 - 0x1118
    # kVA_2 - 0x111A
    # PF_2  - 0x111C 
    async def read_all(self,conn): 
        logger.info(f"Attempting to read all registers for channel two")
        try:
            # Voltage,Current,Power,Reactive_Power,Apparent_Power,Power_Factor
            response = await self.client.read_input_registers(0x1112,12) 
            reg_value = dict.fromkeys(["Volts","Current","kW","kvar","kVA","PF"])
            x,y = 0,2
            for key in reg_value:
                reg_value[key] = (BinaryPayloadDecoder.fromRegisters(response.registers[x:y],Endian.Big, wordorder=Endian.Little )).decode_32bit_float()
                x+=2
                y+=2
            logger.info(f"Succesful read of meter {self.IP}, calling function update_all_values from MySQL.py")
            await MySQL.update_all_values(reg_value,self.IP,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],conn)
        except Exception as e:
            logger.exception("Error in reading all regeisters for channel two")



    ##  read32bitfloat ##
    # Reads a 32 bit float from the smart meter
    # Inputs:
    #   address - The starting address of the 32 bit float
    # Return:
    #   response - A response object from the ModbusTcpClient module  
    async def read32bitfloat(self,address):
        logger.info(f"Reading address:{address} from {self.IP}")
        try:
            response = await self.client.read_input_registers(address, 2)
            time = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            return response, time
        except Exception as e:
            logger.error(f"Error reading {address} from {self.IP}, {e}")
            
  
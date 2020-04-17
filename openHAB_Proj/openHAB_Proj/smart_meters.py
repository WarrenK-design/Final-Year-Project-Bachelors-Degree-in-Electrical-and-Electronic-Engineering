#!/usr/bin/env python


##House Keeping##
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
from pymodbus.client.asynchronous.tcp import AsyncModbusTCPClient as ModbusClient
from pymodbus.client.asynchronous import schedulers
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from openHAB_Proj import MySQL
from datetime import datetime
import logging 
import os

##Set up logger##
#get the logger
logger = logging.getLogger(__name__) #Get the logger
logger.setLevel(logging.INFO) #Set the log level 
#set up the formatting 
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(process)d:%(processName)s:%(filename)s:%(message)s') #Crete a formatter
#setup the file handler 
file_handler = logging.FileHandler('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/smart_meters.log') #Get a file handler
file_handler.setFormatter(formatter)
#setup a stream handler
stream_handler = logging.StreamHandler() # get a stream hander 
stream_handler.setLevel(logging.ERROR) #set the stream handler level 
#Add the handlers to the logger
logger.addHandler(file_handler) #Add the handler to logger 
logger.addHandler(stream_handler)
#os.chmod('/home/openhabian/Environments/env_1/openHAB_Proj/lib/logs/smart_meters.log', 0o777)



class smart_meter():

    ## __init__ ##
    # Initialiase method to intatiated object 
    # Inputs:
    #   IP - The IP address of the smart meter 
    #   client - A modbus client of type 'pymodbus.client.asynchronous.asyncio.ReconnectingAsyncioModbusTcpClient'
    def __init__(self,IP,client):
        #Create the client object passing the IP address of the slave to it 
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
    async def read_all(self,file):
        logger.info(f"Attempting to read all registers for channel two")
        try:
            response = await self.client.read_input_registers(0x1112,12) 
            reg_value = dict.fromkeys(["Volts","Current","kW","kvar","kVA","PF"])
            x,y = 0,2
            for key in reg_value:
                reg_value[key] = (BinaryPayloadDecoder.fromRegisters(response.registers[x:y],Endian.Big, wordorder=Endian.Little )).decode_32bit_float()
                x+=2
                y+=2
            file.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]])
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
            
    ## read_voltage ##
    # Channel two is wired on the meter
    # The voltage for channel two starts at reg 0x1112
    # Return:
    #   Floating point number in volts
    async def read_voltage(self,conn):
        response, time = await self.read32bitfloat(0x1112)
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
            value = decoder.decode_32bit_float()
            logger.info("Attempting to log voltage value to database using MySQL.update_voltage()")
            await MySQL.update_voltage(value,self.IP,time,conn)
        except Exception as e:
            logger.exception(f"Could not decode register response, tracback shown below")

    ## read_current ##
    # Channel two is wired on the meter
    # The current for channel two starts at reg 0x1114
    # Return:
    #   Floating point number in Amps
    async def read_current(self,conn):
        response, time =  await self.read32bitfloat(0x1114)
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
            value = decoder.decode_32bit_float()
            logger.info("Attempting to log current value to database using MySQL.update_current()")
            await MySQL.update_current(value,self.IP,time,conn)
        except Exception as e:
            logger.exception(f"Could not decode register response from reg 0x1114, tracback shown below")

    ## read_kw ##
    # Channel two is wired on the meter
    # The kilo watts channel two starts at reg 0x1116
    # Return:
    #   Floating point number in kw
    async def read_kw(self,conn):
        response, time = await self.read32bitfloat(0x1116)
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
            value = decoder.decode_32bit_float()
            logger.info("Attempting to log power value to database using MySQL.update_power()")
            await MySQL.update_power(value,self.IP,time,conn)
        except Exception as e:
            logger.exception(f"Could not decode register response from reg 0x1116, tracback shown below")


    ## read_kvar ##
    # Channel two is wired on the meter
    # The reactive power channel two starts at reg 0x1118
    # Return:
    #   Floating point number in kvar
    def read_kvar(self):
        response = self.read32bitfloat(0x1118)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
        return decoder.decode_32bit_float()

    ## read_kVA ##
    # Channel two is wired on the meter
    # The kVA channel two starts at reg 0x111A
    # Return:
    #   Floating point number in kVA
    def read_kVA(self):
        response = self.read32bitfloat(0x111A)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
        return decoder.decode_32bit_float()

    ## read_PF2 ##
    # Channel two is wired on the meter
    # The power factor channel two starts at reg 0x1116
    # Return:
    #   Floating point number in volts
    def read_PF2(self):
        response = self.read32bitfloat(0x111C)
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
        return decoder.decode_32bit_float()
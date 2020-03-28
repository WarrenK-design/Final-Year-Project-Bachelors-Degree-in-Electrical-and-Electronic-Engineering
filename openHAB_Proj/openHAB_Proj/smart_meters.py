#!/urs/bin/env python


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
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

#Create the client object passing the IP address of the slave to it 
client = ModbusTcpClient('192.168.0.116')


##  read32bitfloat ##
# Reads a 32 bit float from the smart meter
# Inputs:
#   address - The starting address of the 32 bit float
# Return:
#   response - A response object from the ModbusTcpClient module  
def read32bitfloat(address):
    response = client.read_input_registers(address, 2)
    return response


## read_voltage ##
# Channel two is wired on the meter
# The voltage for channel two starts at reg 0x1112
# Return:
#   Floating point number in volts
def read_voltage():
    response = read32bitfloat(0x1112)
    decoder = BinaryPayloadDecoder.fromRegisters(response.registers, Endian.Big, wordorder=Endian.Little)
    return decoder.decode_32bit_float()
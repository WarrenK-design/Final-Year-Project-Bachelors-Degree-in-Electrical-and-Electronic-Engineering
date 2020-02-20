#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh
#Last edit - 19/02/2020

#This script contains the tests for the open_HAB class 
#The methods testsed in this script are:
#   1. __init__
#   2.get_items
#   3.read_items
#   4.get_switches 


##Librarys to import##
#unittest   - Standard library with functions for unit testing 
#patch      - Class in unittest to mimic objects in tests
#Mock       - Class in unittest to mimic objects in tests 
#OpenHAB    - OpenHAB class for Rest API
#NumberItem - Class for NumberItem typres for Rest API
#SwitchItem - Class for Switch Item types for Rest API 
#sys        - Standard package for directory management 
#open_HAB   - The class which is being tested in this file 


import unittest
from unittest.mock import patch
from unittest.mock import Mock
from openhab.client import OpenHAB
from openhab.items import NumberItem
from openhab.items import SwitchItem
import sys
sys.path.append(r'..')
from openHAB_Proj.open_HAB import open_HAB

class Testopen_HAB(unittest.TestCase):

    ##setUp##
    #Performs initial setup for the tests 
    #This is run for each test 
    #Creates an instance of the open_HAB class
    def setUp(self):
        self.obj = open_HAB()

    ##tearDown##
    #Anything that needs to be reset after a test is complete
    #Should be located in this function 
    def tearDown(self):
        pass

    ##test_initial##
    #Test the intial instance of open_HAB object 
    #from the class being testsed open_HAB
    def test_initial(self):
        self.assertEqual(self.obj.base_url,'http://localhost:8080/rest')
        self.assertEqual(self.obj.items, dict()) 
        self.assertIsInstance(self.obj.openhab,OpenHAB)
        self.assertIsInstance(self.obj.switches,dict)

    
    ##test_get_items##
    #Tests the get_items function 
    #The get_items function calls the fetch_all_items function which is called on
    #a openhab.client.openHAB object which is mocked in this test
    #The return value should be a dictionary with the key being the item name and 
    #the value being the item object
    def test_get_items(self):
        with patch('openhab.client.openHAB') as mock_item:
            temp_items = dict()
            temp_items["Voltage"] = "Voltage_Item"
            mock_item.fetch_all_items.return_value = temp_items
            self.obj.openhab = mock_item
            result = self.obj.get_items()
            self.assertEqual(result["Voltage"],"Voltage_Item")
    
    ##test_read_items##
    #Need to mock NumberItem in this function as state is being read
    #When the state of a number item is read it should read "On"
    #The read_items function returns a dictionary with the item name as 
    #the key and the state as the value
    #In this test the item is "Voltage" and the result should be "On"
    #The function should return a dictionary with "Voltage":""On"
    def test_read_items(self): 
        with patch('openhab.items.NumberItem') as mock_item:
            mock_item.state = "On"
            self.obj.items["Voltage"]=mock_item
            result = self.obj.read_items()
            self.assertEqual(result["Voltage"],"On")
            


    ##test_get_switches##
    #Tests the get switches method 
    #The return from the function should be a dictionary of SwitchItems 
    #The mock_items are of type switch to test this function 
    def test_get_switches(self):
        mock_item1 = Mock(spec = SwitchItem)
        mock_item2 = Mock(spec = SwitchItem)
        self.obj.items["Voltage"] = mock_item1
        self.obj.items["Power"] = mock_item2
        result = self.obj.get_switches()
        self.assertEqual(result["Voltage"],mock_item1)
        self.assertEqual(result["Power"],mock_item2)



if __name__=='__main__':
    unittest.main()




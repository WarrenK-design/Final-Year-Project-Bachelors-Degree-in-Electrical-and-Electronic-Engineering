#!/usr/bin/env python

##House Keeping##
#Author    - Warren Kavanagh 
#Last edit - 11/03/2020

##Description##
#This module contains functions for interfacing with the community_grid database
#It allows connection to the database and to store values in the databases tables
#The database currently contains the following tables:
#   1.Hubs      - Information on each of the hubs in the network
#   2.Devices   - Contains information on the smart devices in the network 
#   3.Items     - Contains information on the items associated with devices in the network



##TODOLIST##


##Modules to import##
# mysql.connector  - Module which contains the functionallity to connect to the MySQL Database
# ConfigParser     - Module to parse configuration files, used to get database config
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser


##Function List##
#   read_db_config - Reads the configuration file for mysql retruns the configuration parameters for in a dictionary
#   connect        - Connects to a mysql database using a config file returned from read_db_config
#   update_items   - Updates an multiple enrtys in the items table at once 
#   insert_items   - Inserts multiple item entrys into the items table, if entrys exists calls the update_items
#   hub_data       - This function populates the hubs table in the database with an entry 
#   insert_device  - Inserts a row into the device table of the community_grid database 


##read_db_config##
#Reads the configuration file for mysql
#retruns the configuration parameters for in a dictionary
#Inputs:
#   filename - The name of the configuration file 
#   section  - The section of the config file to read from 
#Return
#   db  - Configuration parameters to access database in a dictionary 
def read_db_config(filename='/home/openhabian/Environments/env_1/openHAB_Proj/openHAB_Proj/config.ini',section='mysql'):

    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        # Fill the db dictionary with the key and value pairs from
        # the configuration file
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception(f'{section} no found in the {filename} file')
    return db


##connect##
#This connects to a mysql database using a config file
#Calls the function read_db_config which parsers the config.ini file
#Then establishes connection based on the config parameters with the 
#function MySQLConnection
#Return:
#   conn - A MySQLConnection object
def connect():
    db_config = read_db_config()
    conn = None
    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)
        if conn.is_connected():
            return conn
        else:
            print('Connection failed.')

    except Error as error:
        print(error)

##update_item##
#Updates an enrty in the items table 
#An entry will be updated if the table contains a duplicate primary key of ItemUID
#Inputs:
#   item - A list containing tuples of items to update with the ItemUID last 
def update_items(item):
    query = ''' UPDATE items
                SET DeviceID =%s,
                Value = %s,
                Units = %s,
                Time  = %s
                WHERE 
                ItemUID = %s
    '''
    #Try to insert to table
    try:
        conn = connect()
        cursor = conn.cursor()

        # execute the query
        cursor.executemany(query,item)
        # Commit the query 
        conn.commit()
        print("Items Updated")

    #Print the error out
    except Error as e:
      print(e)

    #Close the connection
    finally:
        cursor.close()
        conn.close()

##insert_item##
#Inserts sseveral entrys into the community_grid database table items
#If the entry already exists it will be updated using the update_item
#The item table has the schema 
#+----------+--------------+------+-----+---------+-------+
#| Field    | Type         | Null | Key | Default | Extra |
#+----------+--------------+------+-----+---------+-------+
#| ItemUID  | varchar(255) | NO   | PRI | NULL    |       |
#| DeviceID | varchar(255) | YES  | MUL | NULL    |       |
#| Value    | int          | YES  |     | NULL    |       |
#| Units    | varchar(255) | YES  |     | NULL    |       |
#| Time     | datetime     | YES  |     | NULL    |       |
#+----------+--------------+------+-----+---------+-------+
#Inputs:
#   items - A list contating multiple tuples which have values for ItemUID,DeviceID,Value,Units,Time in that order or single tuple
def insert_item(items):
    query = '''INSERT INTO items(ItemUID,DeviceID,Value,Units,Time)
               VALUES(%s,%s,%s,%s,%s)'''
    #Try to insert to table
    try:
        conn = connect()
        cursor = conn.cursor()

        # execute the query
        cursor.executemany(query,items)
        # Commit the query 
        conn.commit()

    #Print the error out
    except Error as e:
        #The entry is duplicate detected by error code 1062
        if e.errno == 1062:
            print("Entry Exists, updatiing...")
            item = list()
            ID = list()
            # Recorganize each tuple to pass to the update_items function
            # The ItemUID must be last in each tuple, look at the query in update_items function 
            for val in items:
                a = (val[1:5]+(val[0],))
                item.append(a)
            cursor.close()
            conn.close()
            update_items(item)
        else:
            print(e)

    #Close the connection
    finally:
        cursor.close()
        conn.close()

##hub_data##
#This function populates the hubs table in the database
#The hubs table has the following columns 
#| Field         | Type         | Null | Key | Default | Extra |
#+---------------+--------------+------+-----+---------+-------+
#| RaspberryPi_ID | varchar(255) | NO   | PRI | NULL    |       |
#| IP_Address    | varchar(255) | YES  |     | NULL    |       |
#| Location      | varchar(255) | YES  |     | NULL    |       |
#Inputs
    #MAC - The MAC address of the Raaspberry Pi 
    #IP  - The IP address of the Raspberry Pi 
#The Location will have to be manually set as the location of the IP server can only be found
def hub_data(MAC,IP,Time):
    query = '''INSERT INTO hubs(RaspberryPi_ID,IP_Address,Time)
               VALUES(%s,%s,%s)'''
    #Try to insert to table
    try:
        conn = connect()
        cursor = conn.cursor()

        # execute the query
        cursor.execute(query,(MAC,IP,Time))
        # Commit the query 
        conn.commit()

    #Print the error out
    except Error as e:
        #The entry is duplicate detected by error code 1062
        if e.errno == 1062:
            print(f"Entry {MAC} exists, updating entry")
            #Update the value for this primary key
            query = '''UPDATE hubs
                SET IP_Address = %s,
                Time = %s
                WHERE 
                RaspberryPi_ID = %s'''
            try:
                cursor.execute(query,(IP,Time,MAC))
                conn.commit()
            except Error as error:
                print(error)
        else:
            print(e)
    #Close the connection
    finally:
        cursor.close()
        conn.close()


##insert_device##
#This function inserts an entry into the devices table of the community grid database 
#The devices table has the following columns 
#Field                  | Type         | Null | Key | Default | Extra |
#+------------------------+--------------+------+-----+---------+-------+
#| DeviceID               | varchar(255) | NO   | PRI | NULL    |       |
#| RaspberryPi_ID         | varchar(255) | YES  | MUL | NULL    |       |
#| Status                 | varchar(255) | YES  |     | NULL    |       |
#| Status_Detail          | varchar(255) | YES  |     | NULL    |       |
#| Communication_Protocol | varchar(255) | YES  |     | NULL    |       |
#| Binding                | varchar(255) | YES  |     | NULL    |       |
#+------------------------+--------------+------+-----+---------+-------+
def insert_device(DeviceID,RaspberryPi_ID,Status,Status_Detail,Status_Desc,Communication_Protocol,Binding,Time):
    query = ''' INSERT INTO devices(DeviceID,RaspberryPi_ID,Status,Status_Detail,Status_Description,Communication_Protocol,Binding,Time)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
    '''

    #Try to insert to table
    try:
        conn = connect()
        cursor = conn.cursor()

        # execute the query
        cursor.execute(query,(DeviceID,RaspberryPi_ID,Status,Status_Detail,Status_Desc,Communication_Protocol,Binding,Time))
        # Commit the query 
        conn.commit()

    #Print the error out
    except Error as e:
        if e.errno == 1062:
            print(f"Entry {DeviceID} exists, updating entry")
            query = '''UPDATE devices
                SET 
                RaspberryPi_ID =%s,
                Status =%s,
                Status_Detail = %s,
                Status_Description = %s,
                Communication_Protocol = %s,
                Binding =%s,
                Time = %s
                WHERE 
                DeviceID = %s'''
            cursor.execute(query,(RaspberryPi_ID,Status,Status_Detail,Status_Desc,Communication_Protocol,Binding,Time,DeviceID))
            conn.commit()
        else:
            print(e)

    #Close the connection
    finally:
        cursor.close()
        conn.close()


##update_voltage##
#This function will add an entry to the voltage table 
#The schema for the voltage table currently is 
#+-------+--------------+------+-----+---------+----------------+
#| Field | Type         | Null | Key | Default | Extra          |
#+-------+--------------+------+-----+---------+----------------+
#| ID    | int          | NO   | PRI | NULL    | auto_increment |
#| Value | int          | YES  |     | NULL    |                |
#| Units | varchar(255) | YES  |     | Volts   |                |
#| Time  | datetime     | YES  |     | NULL    |                |
#+-------+--------------+------+-----+---------+----------------+
#Inputs:
#   value   - The value of voltage 
#   time    - Time stamp of when the measuremnt was recorded   
def update_voltage(value,time):
    query = ''' INSERT INTO voltages(Value,Time)
                 VALUES(%s,%s)
    '''

    #Try to insert to table
    try:
        conn = connect()
        cursor = conn.cursor()

        # execute the query
        cursor.execute(query,(value,time))
        # Commit the query 
        conn.commit()

    except Error as e:
        print(e)
    
    else:
        print("New entry inserted into voltages table")
    
    finally:
        cursor.close()
        conn.close()











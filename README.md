# Final-Year-Project
This repository is the Python environment for my final year project of an Electrical and Electronic bachelors degree at the Technological University of Dublin. The project looked at creating a soft real time control loop which minimised electrical disturbances on the Irish Grid System through the use of smart metering and smart plugs.

## Background 
This project is in conjunction with an ongoing research project within the Technological University of Dublin, the project is known as the community grid project. Currently in the Irish grid system, if too much electrical energy is generated from microgeneration projects, this can lead to disturbances within the grid system. These disturbances can be minimised by either reducing the amount of energy generated or consuming the excess energy generated. This project looks at developing a prototype for a control loop which detects when too much energy is generated through smart metering and then consuming this energy.

A smart hub which is a combination of both hardware and software that connects devices within a home automation network is developed in this project. The open source software OpenHAB will be used to aid in the development of this smart hub. The hub reads energy levels from connected smart meters to obtain power readings. These power readings are then stored in a remote database which will act as the cloud portion of this project. Based on the power levels in the database, the smart hub will consume electrical energy by turning on wireless smart plugs when required. These are the main tasks within the control loop system which is required to have a loop time of 250 milliseconds or less.

## Repository Structure 
The entire Python virtual environment is stored within this reporsitory. The functionality of the project is stored within the openHAB_Proj directory. A tree diagram of the directory structure of the main components of this directory is shown below. 

![image](https://user-images.githubusercontent.com/61060096/84151524-6c10af00-aa5b-11ea-9744-beb2b7564703.png)

### openHAB_Proj
This is an Python package which contains all the functionality for the control loop implemented. Each file within this package is a module which contains functionality. 

1. AeotechZW096 - This class contains functionality for interfacing with the smart plugs 
2. Open_HAB     - This class contains functionality for interfacing with the OpenHAB REST API 
3. MySQL        - Contains functionality for logging and querying to/from the remote database 
4. smart_meters - Functionality for querying the Modbus smart meters 

### control_loop 
This directory contains the actual implmentation of the control loop using the functions stored within openHAB_Proj. There where two smart meters used within this project the scripts where divided to run on seperate threads for both querying data from the smart meters and logging this data to the remote database. 

1. config - Configuration script used to spawn seperate procceses for each of the control loop scripts 
2. meter_1_log_data - Queried the first modbus smart meter for readings and logged these readings to the remote database 
3. meter_2_log_data - Queried the second modbus smart meter for readings and logged these readings to the remote database 
4. control_loop_one - Queried the remote database for power readings obtained by meter one and actuated the smart plugs within this control loop based on these readings 
5. control_loop_two - Queried the remote database for power readings obtained by meter two and actuated the smart plugs within this control loop based on these readings 

### Remaining Directories
1. lib         - Stores any configuration files and its sub directory log stores the log files generated from each of the scripts 
2. SQL_test    - The implmentation of the tests for measuirng the speed at which data can be stored/queried from the remote database 
3. modbus_test - The implmentation of the tests for measuirng the speed at which data can be queried from the modbus smart meters 
4. zwave_tests - The implmentation of the tests for measuirng the speed at which the Z-Wave smart plugs can be actuated by the control loop  

## Tests of the system 
The data obtained from testing the system was analysed using pandas, numpy and plotted with matplotlib. Below are examples of some of the test results. 

### Z-Wave tests
#### Reading 
The response time for querying the Z-Wave smart plugs for voltage readings was recorded.

![image](https://user-images.githubusercontent.com/61060096/84154255-c7906c00-aa5e-11ea-935b-546945f82d91.png)

#### Writing 
The actuation time of repeatedly toggling the smart plugs was tested. 

![image](https://user-images.githubusercontent.com/61060096/84154332-decf5980-aa5e-11ea-933e-7d6fb19adb39.png)

### Modbus Smart Meter 
The smart meters where tested to see how many connections could be establised to the meters with each connection querying the meter at the same time.

![image](https://user-images.githubusercontent.com/61060096/84154463-0de5cb00-aa5f-11ea-9c97-6053a6fe7d1f.png)

### SQL Database 
#### Reading
The reponse time for querying the remote database for power readings was tested. 

![image](https://user-images.githubusercontent.com/61060096/84154756-66b56380-aa5f-11ea-90d5-7cf4fd267cb7.png)

#### Writing 
The time for logging values to the remote database was tested.

![image](https://user-images.githubusercontent.com/61060096/84154703-57ceb100-aa5f-11ea-81e1-10c4f6f32162.png)

### Control Loop 
The functionality of the control loop was tested. A 5 volt hysteresis margin was added to stop rapid toggling of the smart plugs. If the voltage was above 230 volts the smart plugs where turned on. If the voltage was below 225 volts the smart plugs where turned off. 

![image](https://user-images.githubusercontent.com/61060096/84154812-7765d980-aa5f-11ea-8342-165154ad587a.png)

![image](https://user-images.githubusercontent.com/61060096/84154845-8056ab00-aa5f-11ea-99f2-38ed47b46ab7.png)

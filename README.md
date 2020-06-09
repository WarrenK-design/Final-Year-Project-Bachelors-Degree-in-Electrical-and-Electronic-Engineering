# openHAB_Proj
This repository is the Python environment for my final year project of an Electrical and Electronic bachelors degree at the Technological University of Dublin. The project looked at creating a soft real time control loop which minimised electrical disturbances on the Irish Grid System through the use of smart metering and smart plugs.

## Background 
This project is in conjunction with an ongoing research project within the Technological University of Dublin, the project is known as the community grid project. Currently in the Irish grid system, if too much electrical energy is generated from microgeneration projects, this can lead to disturbances within the grid system. These disturbances can be minimised by either reducing the amount of energy generated or consuming the excess energy generated. This project looks at developing a prototype for a control loop which detects when too much energy is generated through smart metering and then consuming this energy.

A smart hub which is a combination of both hardware and software that connects devices within a home automation network is developed in this project. The open source software OpenHAB will be used to aid in the development of this smart hub. The hub reads energy levels from connected smart meters to obtain power readings. These power readings are then stored in a remote database which will act as the cloud portion of this project. Based on the power levels in the database, the smart hub will consume electrical energy by turning on wireless smart plugs when required. These are the main tasks within the control loop system which is required to have a loop time of 250 milliseconds or less.

## Repository Structure 
The entire Python virtual environment is stored within this reporsitory. The functionality of the project is stored within the openHAB_Proj directory. Within this directory 




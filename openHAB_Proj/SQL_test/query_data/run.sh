#!/bin/sh

./meter_1.py & meter_1_py_pid=$!
./meter_2.py & meter_2_py_pid=$!

echo $meter_1_py_pid
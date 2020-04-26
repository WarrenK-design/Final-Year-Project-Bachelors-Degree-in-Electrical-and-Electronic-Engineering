#!/usr/bin/env python


import subprocess
from subprocess import check_output
print ("start")
subprocess.call("./run.sh", shell=True)
#a = subprocess.call("ps -aux | grep 'python meter_1.py'")
def get_pid(name):
    return check_output(["pidof",name])

print(get_pid("python"))
print ("end")
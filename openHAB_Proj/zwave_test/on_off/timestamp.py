#!/usr/bin/python3.7
import csv
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-f","--file", help="The path to the output file to generate a timestamp to")
parser.add_argument("-v","--val", help="Value of the switch either ON or OFF")
args = parser.parse_args()
file_name = (args.file)
val = args.val

with open(file_name, mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],val])
        print(f"New Timestamp in {file_name}")
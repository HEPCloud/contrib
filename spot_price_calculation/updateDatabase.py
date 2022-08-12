from __future__ import print_function
from SpotPriceHistory import SpotPriceHistory
import datetime
import os.path
from analysis import simulation
import sys

instances=["m3.2xlarge","c3.2xlarge","c3.xlarge","c4.xlarge", "m4.xlarge","c4.2xlarge", "m4.2xlarge","m3.medium","m3.large","m3.xlarge","c3.large","c3.4xlarge","c3.8xlarge","m4.4xlarge","m4.10xlarge","c4.4xlarge","c4.8xlarge","r3.large", "r3.xlarge","r3.2xlarge","r3.4xlarge","r3.8xlarge", "c5.4xlarge", "c5a.4xlarge", "c6i.4xlarge", "c6a.4xlarge", "m5.4xlarge", "m5a.4xlarge", "m6i.4xlarge", "m6a.4xlarge", "r5.4xlarge", "r5a.4xlarge", "r6i.4xlarge"]
zone=["us-east-1b", "us-east-1c","us-east-1d","us-west-1a","us-west-1c","us-west-2a", "us-west-2b","us-west-2c"]

if not os.path.exists("Database"):
    os.mkdir("Database")
if not os.path.exists("Histogram"):
    os.mkdir("Histogram")


for i in instances:
    for z in zone:
        try:
            awsPrice=SpotPriceHistory(i,z)
            awsPrice.getSpotPriceHistory()
#	    awsPrice.printHistoryData()
            awsPrice.writeHistoryData()
            analyze=simulation(i,z)
            analyze.writeHistogram()
            print(i + " in " + z +" finishes!")
        except:
            print("Error:", sys.exc_info()) 

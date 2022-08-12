from __future__ import print_function
from builtins import str
import datetime
import os
import sys

instances=["m3.2xlarge","c3.2xlarge","c3.xlarge","c4.xlarge", "m4.xlarge","c4.2xlarge", "m4.2xlarge","m3.medium","m3.large","m3.xlarge","c3.large","c3.4xlarge","c3.8xlarge","m4.4xlarge","m4.10xlarge","c4.4xlarge","c4.8xlarge","r3.large", "r3.xlarge","r3.2xlarge","r3.4xlarge","r3.8xlarge", "c5.4xlarge", "c5a.4xlarge", "c6i.4xlarge", "c6a.4xlarge", "m5.4xlarge", "m5a.4xlarge", "m6i.4xlarge", "m6a.4xlarge", "r5.4xlarge", "r5a.4xlarge", "r6i.4xlarge"]
zone=["us-west-2a", "us-west-2b","us-west-2c","us-west-1a","us-west-1c","us-east-1b", "us-east-1c","us-east-1d"]

def checkDatabase(filename):
        '''
        read last time stamp from the Database, and set start time and end time
        '''

        if not os.path.isfile(filename):
            print ("File does not exist! ")          
        else:
            listOfLines=[]
            with open(filename,"r") as f:
                lastTime=datetime.datetime.utcnow()-datetime.timedelta(days=720)
                lineNo=1
                error=0
                for lines in f:
                    try:
                        tempStr=lines.split(" ")
                        currentTime=datetime.datetime.strptime(tempStr[0],"%Y-%m-%dT%H:%M:%S.%f")
                        float(tempStr[1])
			if (currentTime-lastTime).total_seconds()<0:
                            print(filename+" "+str(lineNo)+" \n")
                            error+=1
                        else:
                            listOfLines.append(lines)
                            lastTime=currentTime
                        lineNo+=1
                    except:
			error+=1
                        #listOfLines.append(lines)
                        print(sys.exc_info())
            f.close()
            if error>0:
                f=open(filename,"w")
                for lines in listOfLines:
                    f.write(lines)
                f.close()
#         self.startTime=self.startTime.replace(tzinfo=None)
#         for tt in self.startTime.timetuple():
#             print tt
path=sys.argv[1]+'/'
for i in instances:
    for z in zone:
        filename=path+i+"_"+z
        checkDatabase(filename)
	print(filename+" finished!")

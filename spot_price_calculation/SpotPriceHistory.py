from __future__ import print_function

from builtins import str
from builtins import object
import boto3
import datetime
import os.path
from boto3.session import Session

class SpotPriceHistory(object):
    '''
    This class is used for getting spot pricing history
    '''

    startTime = ""
    endTime = ""
    zone = "us-west-2a"
    instanceType="m3.medium"
    os="Linux/UNIX"
    #historyData = {}
    #dataList=[]
    # specialInstance=["c4.xlarge", "c4.2xlarge","c4.4xlarge","c4.8xlarge","m4.xlarge", "m4.2xlarge","m4.4xlarge","m4.10xlarge"]
    # specialZones=["us-east-1b", "us-east-1c","us-east-1d"]
    specialZones=[]

    nextToken=""
    def __init__(self,instanceType,zone):
        self.instanceType=instanceType
        self.zone=zone
        self.historyData={}
        self.dataList=[]
        self.filename="Database/"+self.instanceType+"_"+self.zone
        self.readLastTimeFromDatabase()
#     def __init__(self, startTime, endTime):
#         '''
#         Constructor
#         '''
#         self.startTime=startTime
#         self.endTime=endTime
    
    def set_startTime(self,startTime):
        self.startTime=startTime
    def set_endTime(self,endTime):
        self.endTime=endTime
    def set_zone(self,zone):
        self.zone=zone
    def set_instanceType(self,instanceType):
        self.instanceType=instanceType
    def set_os(self,os):
        self.os=os
    def ifValidEntry(self, entry):
        try:
            if entry['Timestamp']==None or entry['SpotPrice']==None:
                return False
            float(entry['SpotPrice'])
            return True
        except:
            return False    
    
    def obtainRoleBasedSession(self):
        """ Obtain a short-lived role-based token
        """
        roleNameString = 'ReadEC2SpotPrice'
        fullRoleNameString = 'arn:aws:iam::159067897602:role/' + roleNameString

        # using boto3 default session to obtain temporary token
        # long term credentials have ONLY the permission to assume role CalculateBill
        client = boto3.client('sts')
        response = client.assume_role( RoleArn=fullRoleNameString, RoleSessionName='roleSwitchSession'  )

        role_AK_id = response['Credentials']['AccessKeyId']
        role_AK_sc = response['Credentials']['SecretAccessKey']
        role_AK_tk = response['Credentials']['SessionToken']
        
        session = Session(aws_access_key_id=role_AK_id, aws_secret_access_key=role_AK_sc, aws_session_token=role_AK_tk,region_name=self.zone[:-1]) 
        return session 
    
    def getSpotPriceHistory(self):
        session= self.obtainRoleBasedSession()
        # boto3.session.Session(region_name=self.zone[:-1])
        client = session.client("ec2")
        iterates=0
#        if self.zone in self.specialZones:
#            self.os="Linux/UNIX (Amazon VPC)"
#        else:
        self.os="Linux/UNIX"
        while iterates==0 or self.nextToken!="" :
            temp = client.describe_spot_price_history(
                DryRun=False,
                StartTime=self.startTime,
                EndTime=self.endTime,
                InstanceTypes=[self.instanceType],
                ProductDescriptions=[self.os],
                Filters=[],
                AvailabilityZone= self.zone,
                MaxResults=1000,
                NextToken=self.nextToken
             )
            self.dataList.insert(0, temp)
#             tempDic=self.historyData.copy()
#             tempDic.update(temp)
#             self.historyData=tempDic
            self.nextToken=temp['NextToken']
            iterates+=1
    def printHistoryData(self):
        for dicts in self.dataList:
            for i in reversed(dicts['SpotPriceHistory']):
                print((i['InstanceType'],i['ProductDescription'],i['SpotPrice'],str(i['Timestamp']),i['AvailabilityZone']))
            
    def getCredentials(self):
        '''
        Get AWS credentials from file
        '''
        
    def writeHistoryData(self):
        '''
        Write the historical data into database
        '''
        filename=self.filename
        if not os.path.isfile(filename):
            f=open(filename,"w")
            f.write("DateTime Price InstanceType Zone\n")
            last=self.startTime
            for dicts in self.dataList :
                for i in reversed(dicts['SpotPriceHistory']):
                    current=i['Timestamp'].replace(tzinfo=None)
                    if current>last and self.ifValidEntry(i):
                        f.write(i['Timestamp'].strftime("%Y-%m-%dT%H:%M:%S.%f")+" "+str(i['SpotPrice'])+" "+str(i['InstanceType'])+" "+str(i['AvailabilityZone'])+"\n")
                    last=current
            f.close()
        else:
            f=open(filename,"a")
            last=self.startTime
            for dicts in self.dataList :
                for i in reversed(dicts['SpotPriceHistory']):
#                 for t in i['Timestamp'].timetuple():
#                     print t      
#                 for tt in self.startTime.timetuple():
#                     print tt
                    current=i['Timestamp'].replace(tzinfo=None)
                    if current>last and self.ifValidEntry(i):
                        f.write(i['Timestamp'].strftime("%Y-%m-%dT%H:%M:%S.%f")+" "+str(i['SpotPrice'])+" "+str(i['InstanceType'])+" "+str(i['AvailabilityZone'])+"\n")
                    last=current
            f.close()
            
        
    def readLastTimeFromDatabase(self):
        '''
        read last time stamp from the Database, and set start time and end time
        '''
        self.endTime=datetime.datetime.utcnow()
        filename = self.filename
        if not os.path.isfile(filename):
            print ("File does not exist! Start from 90 days ago!")
            self.startTime=self.endTime-datetime.timedelta(days=90)
            
        else:
            with open(filename,"r") as f:
                for lines in f:
                    pass
                last=lines
                #content=f.read().splitlines()
            #tempStr=content[len(content)-2].split(" ")
            tempStr=last.split(" ")
            print("Last time stamp: " + tempStr[0])
            self.startTime=datetime.datetime.strptime(tempStr[0],"%Y-%m-%dT%H:%M:%S.%f")
            f.close()
#         self.startTime=self.startTime.replace(tzinfo=None)
#         for tt in self.startTime.timetuple():
#             print tt


vCPUs = {
    'c3.large'   :2,
    'c3.xlarge'  :4,
    'c3.2xlarge' :8,
    'c3.4xlarge' :16,
    'c3.8xlarge' :32,
    'c4.large'   :2,
    'c4.xlarge'  :4,
    'c4.2xlarge' :8,
    'c4.4xlarge' :16,
    'c4.8xlarge' :32,
    'c5.4xlarge' :16,
    'c5a.4xlarge':16,
    'c6i.4xlarge':16,
    'c6a.4xlarge':16,
    'm3.medium'  :1,
    'm3.large'   :2,
    'm3.xlarge'  :4,
    'm3.2xlarge' :8,
    'm4.large'   :2,
    'm4.xlarge'  :4,
    'm4.2xlarge' :8,
    'm4.4xlarge' :16,
    'm4.10xlarge':40,
    'm5.4xlarge' :16,
    'm5a.4xlarge':16,
    'm6i.4xlarge':16,
    'm6a.4xlarge':16,
    'r3.large'   :2,
    'r3.xlarge'  :4,
    'r3.2xlarge' :8,
    'r3.4xlarge' :16,
    'r3.8xlarge' :32,
    'r5.4xlarge' :16,
    'r5a.4xlarge':16,
    'r6i.4xlarge':16
}

ecu = {
    'c3.large'   :7,
    'c3.xlarge'  :14,
    'c3.2xlarge' :28,
    'c3.4xlarge' :55,
    'c3.8xlarge' :108,
    'c4.large'   :8,
    'c4.xlarge'  :16,
    'c4.2xlarge' :31,
    'c4.4xlarge' :62,
    'c4.8xlarge' :132,
    'c5.4xlarge' :77,
    'c5a.4xlarge':67,
    'c6i.4xlarge':80,
    'c6a.4xlarge':71,
    'm3.medium'  :3,
    'm3.large'   :6.5,
    'm3.xlarge'  :13,
    'm3.2xlarge' :26,
    'm4.large'   :6.5,
    'm4.xlarge'  :13,
    'm4.2xlarge' :26,
    'm4.4xlarge' :53.5,
    'm4.10xlarge':124.5,
    'm5.4xlarge' :65,
    'm5a.4xlarge':42,
    'm6i.4xlarge':77,
    'm6a.4xlarge':67,
    'r3.large'   :6.5,
    'r3.xlarge'  :13,
    'r3.2xlarge' :26,
    'r3.4xlarge' :52,
    'r3.8xlarge' :104,
    'r5.4xlarge' :58,
    'r5a.4xlarge':37,
    'r6i.4xlarge':66
}

std_prices = {
    'c3.large'   :0.105,
    'c3.xlarge'  :0.210,
    'c3.2xlarge' :0.420,
    'c3.4xlarge' :0.840,
    'c3.8xlarge' :1.680,
    'c4.large'   :0.11,
    'c4.xlarge'  :0.22,
    'c4.2xlarge' :0.441,
    'c4.4xlarge' :0.796,
    'c4.8xlarge' :1.763,
    'c5.4xlarge' :0.680,
    'c5a.4xlarge':0.616,
    'c6i.4xlarge':0.680,
    'c6a.4xlarge':0.612,
    'm3.medium'  :0.070,
    'm3.large'   :0.140,
    'm3.xlarge'  :0.280,
    'm3.2xlarge' :0.560,
    'm4.large'   :0.126,
    'm4.xlarge'  :0.252,
    'm4.2xlarge' :0.504,
    'm4.4xlarge' :0.800,
    'm4.10xlarge':2.52,
    'm5.4xlarge' :0.768,
    'm5a.4xlarge':0.688,
    'm6i.4xlarge':0.768,
    'm6a.4xlarge':0.691,
    'r3.large'   :0.175,
    'r3.xlarge'  :0.35,
    'r3.2xlarge' :0.7,
    'r3.4xlarge' :1.4,
    'r3.8xlarge' :2.8,    
    'r5.4xlarge' :1.008,
    'r5a.4xlarge':0.904,
    'r6i.4xlarge':1.008
}

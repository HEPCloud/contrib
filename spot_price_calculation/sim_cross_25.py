from __future__ import print_function
from __future__ import division
from builtins import str
from past.utils import old_div
from SpotPriceHistory import SpotPriceHistory
import datetime
from analysis import *
import os.path
from amazing import *
from SpotPriceHistory import std_prices
import adaptive_bid
import numpy
import sys


if not len(sys.argv)==4:
    print("arguments: jobExecutionTime(Hours)  ifContinueExecution (1: continue, 0:checkpointing)   AlgorithmSet( 1: All other, 0:Amazing) ")
    exit()

instances=["m3.2xlarge","c3.2xlarge","c3.xlarge","c4.xlarge", "m4.xlarge","c4.2xlarge", "m4.2xlarge","m3.medium","m3.large","m3.xlarge","c3.large","c3.4xlarge","c3.8xlarge","m4.4xlarge","m4.10xlarge","c4.4xlarge","c4.8xlarge","r3.large", "r3.xlarge","r3.2xlarge","r3.4xlarge","r3.8xlarge", "c5.4xlarge", "c5a.4xlarge", "c6i.4xlarge", "c6a.4xlarge", "m5.4xlarge", "m5a.4xlarge", "m6i.4xlarge", "m6a.4xlarge", "r5.4xlarge", "r5a.4xlarge", "r6i.4xlarge"]
zone=["us-west-2a", "us-west-2b","us-west-2c","us-west-1a","us-west-1c","us-east-1b", "us-east-1c","us-east-1d"]
#instances=["c4.xlarge","c4.2xlarge"]
#zone=["us-east-1b","us-west-2a"]

algNames=["Demandx.25"]

simulationLength = 2*3600
jobExecution = int(sys.argv[1])*3600
jobDeadline = 7*24 * 3600
resumeOverhead = 60
checkOverhead = 120
if not int(sys.argv[2])==0:
    continuesExe=True
else:
    continuesExe=False
debug=False
topDebug=False
FullStatList=[]
        
def calStat(result_list):
    maxP=0.
    minP=float("inf")
    sumC=0.0
    sumC_Suc=0.0
    successNo=0.0
    miss_deadline=0.0
    miss_now=0.0
    maxW=0.0
    minW=float("inf")
    sumW=0.0
    sumWSuc=0.0
    count=0
    num_of_immediateStart=0.0
    sum_no_of_failure=0.0
    zoneStat={}
    for z in zone:
        zoneStat[z]=0.0
    for i in result_list:
        price=i[0]
        waitT=i[1]-i[2]
        if i[1]>jobDeadline or i[1]==0 or i[2]<jobExecution:
            miss_deadline+=1
        else:
            successNo+=1
            sumC_Suc+=price
            
            sumWSuc+=waitT
        if not  i[1]-i[2]<=resumeOverhead or i[2]<jobExecution :
            miss_now+=1
        if i[1]>=0:
            count+=1
            sumC+=price
            
            sumW+=waitT
            sum_no_of_failure+=i[7]
        if price>=maxP:
            maxP=price
        if price<=minP and not price==0:
            minP=price
        if waitT>=maxW:
            maxW=waitT
        if waitT<=minW:
            minW=waitT
        if i[6]==True:
            num_of_immediateStart+=1
        zoneStat[i[8]]+=1
      
    miss_deadline=old_div(miss_deadline,len(result_list))
    miss_now = old_div(miss_now,len(result_list))
    immediateStartRate = old_div(num_of_immediateStart,len(result_list))
    
    '''
    return AveCost,  MaxCost, MinCost, AveWait, MaxWait, MinWait, DeadlineMissRate, FailureRate, ImmediateStartRate, NoOfFailure, AveSuccessCost, AveSuccessCostTotal
    '''
    return (old_div(sumC,count), maxP, minP, old_div(sumWSuc,count),maxW, minW, miss_deadline, miss_now, immediateStartRate, old_div(sum_no_of_failure,count), old_div(sumC_Suc,successNo) if successNo>0 else 0, old_div(sumC,successNo) if successNo>0 else 0,zoneStat)

def calMostEffZone(result_list):
    eff=()
    minPrce=float("inf")
    miss=True
    for i in result_list:
        if i[1]>jobDeadline or i[1]==0 or i[2]<jobExecution:
            deadlineMiss=True
        else:
            deadlineMiss=False
        if miss==False and deadlineMiss==True:
            continue
        else:
            if i[0]<=minPrce:
                eff=i
                minPrce=i[0]
                miss=deadlineMiss
    return eff

if not os.path.exists("Database"):
    os.mkdir("Database")
if not os.path.exists("Histogram"):
    os.mkdir("Histogram")
if not os.path.exists("Simulation"):
    os.mkdir("Simulation")
if not os.path.exists("SimulationCross"):
    os.mkdir("SimulationCross")
if not os.path.exists("SimulationCross_25"):
    os.mkdir("SimulationCross_25")
timstamp=datetime.datetime.utcnow()
SimDetailPath="SimulationCross_25/Detail-"+timstamp.strftime("%Y-%m-%d")
SimBarchartPath="Simulation/Bar"
caseStr="_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]
StatFull=timstamp.strftime("%Y-%m-%d")+"-SimulationTotalResultCrossZones_25"+caseStr
if not os.path.exists(SimDetailPath):
    os.mkdir(SimDetailPath)
if not os.path.exists(SimBarchartPath):
    os.mkdir(SimBarchartPath)

priceHistory={}

ABSendTime=datetime.datetime.utcnow()
startTime=ABSendTime-timedelta(days=90)
simulationLength=jobDeadline+1
endTime=startTime+timedelta(seconds=simulationLength)

statistics={}
final_res_list={}

for i in instances:
    for z in zone:
        try:
            priceHistory[i+z]=simulation(i,z,startTime,ABSendTime)
        except:
            continue
        
for i in instances:
    statistics[i]={}
    final_res_list[i]={}
    for names in algNames:
        statistics[i][names]= {"AveCost":0.0, "MaxCost":0.0, "MinCost":0.0, "CostToDemandRate":0.0, "AveWaiting": 0.0 ,
                                 "MaxWaiting":0.0,  "MinWaiting": 0.0, "DeadlineMissRate":0.0, "FailureRate":0.0 , 
                                 "ImmediateStartRate":0.0, "NoOfFailure":0.0, "SuccessCostToDemandRate":0.0, "SuccessTotalCostToDemandRate":0.0}
        final_res_list[i][names]=[]
        for z in zone:
            statistics[i][names][z]=0.0
    if continuesExe:
        filePath = SimDetailPath+"/"+i+"_continues"+caseStr
    else:
        filePath = SimDetailPath+"/"+i+caseStr
    f=open(filePath,"w")
    f.write("Statistics Information for Instance "+i+":\n")
    f.close()
num_of_jobs = numpy.ceil(old_div((ABSendTime-startTime).total_seconds(),3600))
print("start")
jobCount=1
while startTime<ABSendTime-timedelta(seconds=jobDeadline):
#while startTime<ABSendTime-timedelta(days=89.9):
    endTime=startTime+timedelta(seconds=jobDeadline+1)
    
    jobStartTime=datetime.datetime.utcnow()
    jobEndTime=jobStartTime
    for i in instances:
        res_List={}
        for names in algNames:
            res_List[names]=[]
        for z in zone:
            countStartTime= datetime.datetime.utcnow()
            try:
                sim=priceHistory[i+z]
            except:
                continue
            priceMax=sim.maxPrice()
            priceMin=sim.minPrice()
            demandPrice=std_prices[i]
            startPrice=sim.fullData[0][1]
 
        
            def SimulationDeadline(startTime, price):
                SimStartTime=startTime
                resubmitFrequency=3600
                failure=0
                cost=0.0
                totalExe=0.0
                realExe=0.0
                simDuration=jobDeadline
                etime=startTime+datetime.timedelta(seconds=jobDeadline)
                index=1
                while SimStartTime < etime:                
                    tmpRes=sim.simulation(SimStartTime, simDuration, price, jobExecution, simDuration, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                    cost+=tmpRes[0]
                    totalExe+=tmpRes[1]
                    if tmpRes[2]>0:
                        realExe=tmpRes[2]
                    if tmpRes[2]<jobExecution:
                        failure+=1
                    if index==1:
                        immedStart=tmpRes[6]
                        index+=1
                    simDuration=jobDeadline - tmpRes[1]-resubmitFrequency
                    SimStartTime = SimStartTime+datetime.timedelta(seconds=tmpRes[1]+resubmitFrequency)
                    if realExe >= jobExecution:
                        break
                
                return (cost,totalExe,realExe, 0,0,0,immedStart,failure,sim.zone)
            
            count=1    
            
            while count<2:
                try:
                    simulationLength=(endTime-startTime).total_seconds()
                    
                    countEndTime=countStartTime
                    if not int(sys.argv[3])==0:
                  
                        if not continuesExe:
                            result_demandx25=sim.simulation(startTime, simulationLength, demandPrice*0.25, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                        else:
                            result_demandx25=SimulationDeadline(startTime, demandPrice*0.25)
                        res_List["Demandx.25"].append(result_demandx25)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("0.25xDemand: "+str(timeLap))
                            print("Bid Demand x 0.25: " + str(startTime)+" "+str(result_demandx25)+"\n")                
 
                    
                    countEndTime=datetime.datetime.utcnow()
                    timeLap=(countEndTime-countStartTime).total_seconds()
                
                    #print i+" in "+ z + " finished, using: "+str(timeLap)
                    startPrice = sim.fullData[sim.findIndex(startTime)][1]
                    count+=1
                    #startTime+=timedelta(seconds=3600)
                except:
                    print("Unexpected error:", sys.exc_info())
        
        d_line=str(startTime)+" "
        for names in algNames:
            tmpMEZ=calMostEffZone(res_List[names])
            final_res_list[i][names].append(tmpMEZ)
            d_line+=names+" "+str(tmpMEZ)+" "
        d_line+="\n"
        if continuesExe:
            filePath = SimDetailPath+"/"+i+"_continues"+caseStr
        else:
            filePath = SimDetailPath+"/"+i+caseStr
        
        f=open(filePath,"a")
        f.write(d_line)
        f.close()
    jobEndTime=datetime.datetime.utcnow()
    timeLap=(jobEndTime-jobStartTime).total_seconds()
    print(str(jobCount)+"/"+str(num_of_jobs)+" using: "+str(timeLap))
    jobCount+=1
    startTime+=timedelta(seconds=3600)

for i in instances:
    demandCost = numpy.ceil(old_div(jobExecution,3600))*std_prices[i]
    for names in algNames:
        statMin=calStat(final_res_list[i][names])
        statistics[i][names]["AveCost"] = statMin[0]
        statistics[i][names]["MaxCost"] = statMin[1]
        statistics[i][names]["MinCost"] = statMin[2]
        statistics[i][names]["CostToDemandRate"] = old_div(statMin[0],demandCost)
        statistics[i][names]["AveWaiting"] = statMin[3]
        statistics[i][names]["MaxWaiting"] = statMin[4]
        statistics[i][names]["MinWaiting"] = statMin[5]
        statistics[i][names]["DeadlineMissRate"] = statMin[6]
        statistics[i][names]["FailureRate"] = statMin[7]
        statistics[i][names]["ImmediateStartRate"]=statMin[8]
        statistics[i][names]["NoOfFailure"]=statMin[9]
        statistics[i][names]["SuccessCostToDemandRate"]=old_div(statMin[10],demandCost)
        statistics[i][names]["SuccessTotalCostToDemandRate"]=old_div(statMin[11],demandCost)
        for z in zone:
            statistics[i][names][z]=statMin[12][z]

    keyList=list(statistics[i][algNames[0]].keys())

    if not os.path.exists(StatFull):
        f=open(StatFull,"a")
        line="InstanceType   "
        for j in algNames:
            for k in keyList:
                line+=j+"_"+k+"    "
        line+="\n"
        f.write(line)
    else:
        f=open(StatFull,"a")
            

    line=i+"    "
    for j in algNames:
        for k in keyList:
            line+=str(statistics[i][j][k])+"    "
    line+="\n"
    f.write(line)
    f.close()
    print(i+" finished!\n")
print("Finish simulation!")
print("Start draw bar charts")


print("All done!")

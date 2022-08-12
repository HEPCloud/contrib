from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range
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
#instances=["m3.medium"]
#zone=["us-east-1b"]
if not int(sys.argv[3])==0:
    algNames=["Demandx.50"]
else:
    algNames=["AmazingBid"]
    
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
    print("calStat running!\n")
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
    sumRealExe=0.0
    for i in result_list:
        price=i[0]
        waitT=i[1]-i[2]
        sumRealExe+=i[8]
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
      
    miss_deadline=old_div(miss_deadline,len(result_list))
    miss_now = old_div(miss_now,len(result_list))
    immediateStartRate = old_div(num_of_immediateStart,len(result_list))
    
    '''
    return AveCost,  MaxCost, MinCost, AveWait, MaxWait, MinWait, DeadlineMissRate, FailureRate, ImmediateStartRate, NoOfFailure, AveSuccessCost, AveSuccessCostTotal, AveRealExecution
    '''
    return (old_div(sumC,count), maxP, minP, old_div(sumWSuc,count),maxW, minW, miss_deadline, miss_now, immediateStartRate, old_div(sum_no_of_failure,count), old_div(sumC_Suc,successNo) if successNo>0 else 0, old_div(sumC,successNo) if successNo>0 else 0, old_div(sumRealExe,count))


if not os.path.exists("Database"):
    os.mkdir("Database")
if not os.path.exists("Histogram"):
    os.mkdir("Histogram")
if not os.path.exists("Simulation"):
    os.mkdir("Simulation")
if not os.path.exists("SimulationResults"):
    os.mkdir("SimulationResults")
SimDetailPath="Simulation/Detail"
SimBarchartPath="Simulation/Bar"
caseStr="_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]
StatFull="SimulationResults/SimulationTotalResult"+caseStr+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
if not os.path.exists(SimDetailPath):
    os.mkdir(SimDetailPath)
if not os.path.exists(SimBarchartPath):
    os.mkdir(SimBarchartPath)

def DrawBarChart(statistic):
    import matplotlib.pyplot as plt
    
    print("DrawBarChart running!\n")
    N = len(algNames)
    
    failureRate=[]
    deadlineMiss=[]
    costToDemand=[]
    immediateStart=[]
    costToDemandSuc=[]
    costSucTotalToDemand=[]
#    noOfFailure=[]
    for alg in algNames:
        failureRate.append(statistic[alg]["FailureRate"]) 
        deadlineMiss.append(statistic[alg]["DeadlineMissRate"])
        costToDemand.append( statistic[alg]["CostToDemandRate"])
        immediateStart.append( statistic[alg]["ImmediateStartRate"])
        costToDemandSuc.append(statistic[alg]["SuccessCostToDemandRate"])
        costSucTotalToDemand.append(statistic[alg]["SuccessTotalCostToDemandRate"])
#        noOfFailure.append(statistic[alg]["NoOfFailure"])
    ind = numpy.arange(N)  # the x locations for the groups
    width = 0.15      # the width of the bars

    fig = plt.figure(figsize=(20,9))
    ax = fig.add_subplot(111)
    rects1 = ax.bar(ind, failureRate, width, color='r')
    rects2 = ax.bar(ind+width, deadlineMiss,width, color='b')   
    rects3 = ax.bar(ind+2*width, immediateStart, width, color="g")
    rects4 = ax.bar(ind+3*width, costToDemand, width, color="y")
    rects5 = ax.bar(ind+4*width,costToDemandSuc,width, color="k")
    rects6 = ax.bar(ind+5*width,costSucTotalToDemand,width, color="m")
    # add some text for labels, title and axes ticks
    #plt.ylim(0,1.2)
    ax.set_ylabel('Percentage')
    ax.set_title(statistic["Instance"]+"_"+statistic["Zone"]+caseStr, y=1.06)
    l=ax.set_xticks(ind+width)
    ax.set_xticklabels( algNames, rotation=30)
    ax.legend( (rects1[0], rects2[0], rects3[0], rects4[0],rects5[0],rects6[0]), ('FailureRate', 'DeadlineMissRate', 'ImmediateStartRate', 'CostToDemandRateTotal', 'CostToDemandRateSuccess', 'CostToDemandRatePerSuccess'),
                bbox_to_anchor=(0., 1.01, 1., .101), loc=3,ncol=3, mode="expand", borderaxespad=0. )
#    ax.legend( (rects1[0], rects2[0], rects3[0], rects4[0]), ('FailureRate', 'DeadlineMissRate', 'ImmediateStartRate', 'CostToDemandRate'),
#                bbox_to_anchor=(0., 1.01, 1., .101), loc=3,ncol=4, mode="expand", borderaxespad=0. )
    def autolabelp(rects):
        print("autolabelp running!\n")
    # attach some text labels
        for rect in rects:
            height = rect.get_height()
            pStr= "{0:10.2f}".format(height*100)+"%"
            ax.text(rect.get_x()+rect.get_width()/2., 0.99*height, pStr ,
                ha='center', va='bottom',rotation=90)
    def autolabel(rects):
    # attach some text labels
        for rect in rects:
            height = rect.get_height()
            pStr= "{0:10.2f}".format(height)
            ax.text(rect.get_x()+rect.get_width()/2., 0.99*height, pStr ,
                ha='center', va='bottom',rotation=90)
    autolabelp(rects1)
    autolabelp(rects2)
    autolabelp(rects3)
    autolabelp(rects4)
    autolabelp(rects5)
    autolabelp(rects6)
    plt.show()
   # plt.savefig(SimBarchartPath+"/"+statistic["Instance"]+"_"+statistic["Zone"]+caseStr+".png")


#st=datetime.datetime.utcnow()    
#global_min_price_per_ecu=getMinPricePerECU(instances,zone)
#et=datetime.datetime.utcnow()
#df=(et-st).total_seconds()
#print "Getting min ecu price using: "+str(df)+" seconds!"

for i in instances:
    for z in zone:
        statistics={"Instance" : i, "Zone" : z}
        res_List={}
        for names in algNames:
            res_List[names]=[]
            statistics[names]= {"AveCost":0.0, "MaxCost":0.0, "MinCost":0.0, "CostToDemandRate":0.0, "AveWaiting": 0.0 ,
                                 "MaxWaiting":0.0,  "MinWaiting": 0.0, "DeadlineMissRate":0.0, "FailureRate":0.0 , 
                                 "ImmediateStartRate":0.0, "NoOfFailure":0.0, "SuccessCostToDemandRate":0.0, "SuccessTotalCostToDemandRate":0.0, "AveRealExeTime":0.0}
        try:
            sim=simulation(i,z)
        except:
            continue
        if len(sim.fullData)==0:
            continue
        priceMax=sim.maxPrice()
        priceMin=sim.minPrice()
        demandPrice=std_prices[i]
        startPrice=sim.fullData[0][1]
        startTime= sim.fullData[0][0]
        endTime=sim.fullData[len(sim.fullData)-1][0]
        startTime=endTime-timedelta(days=90)
#        endTime=startTime+timedelta(hours=200)
        simulationLength=(endTime-startTime).total_seconds()
        
        def SimulationDeadline(startTime, price):
            SimStartTime=startTime
            resubmitFrequency=3600
            failure=0
            cost=0.0
            totalExe=0.0
            realExe=0.0
            totalRealExe=0.0
            simDuration=jobDeadline
            etime=startTime+datetime.timedelta(seconds=jobDeadline)
            index=1
            while SimStartTime < etime:                
                tmpRes=sim.simulation(SimStartTime, simDuration, price, jobExecution, simDuration, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                cost+=tmpRes[0]
                totalExe+=tmpRes[1]
                totalRealExe+=tmpRes[2]
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
                
            return (cost,totalExe,realExe, 0,0,0,immedStart,failure,totalRealExe)
        num_of_jobs = numpy.ceil(old_div((simulationLength-jobDeadline),3600))
        count=1    
        
        print("start")
        while startTime<endTime-datetime.timedelta(seconds=jobDeadline):
            try:
                simulationLength=(endTime-startTime).total_seconds()
                countStartTime= datetime.datetime.utcnow()
                countEndTime=countStartTime
                timeLap=0
                if not int(sys.argv[3])==0:
                   
                    if not continuesExe:
                        result_demandx50=sim.simulation(startTime, simulationLength, demandPrice*0.5, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                    else:
                        result_demandx50=SimulationDeadline(startTime, demandPrice*0.5)
                    res_List["Demandx.50"].append(result_demandx50)
                    timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                    countEndTime=datetime.datetime.utcnow()                
                    if topDebug:
                        print("0.50xDemand: "+str(timeLap))
                        print("Bid Demand x 0.50: " + str(startTime)+" "+str(result_demandx50)+"\n")                
 
                startTime+=timedelta(seconds=3600)
                countEndTime=datetime.datetime.utcnow()
                timeLap=(countEndTime-countStartTime).total_seconds()    
                print(str(count)+"/"+str(num_of_jobs) + " using: "+str(timeLap))
                startPrice = sim.fullData[sim.findIndex(startTime)][1]
                count+=1
            except:
                print("Unexpected error:", sys.exc_info())
        demandCost = numpy.ceil(old_div(jobExecution,3600))*std_prices[i]
        for names in algNames:
            statMin=calStat(res_List[names])
            statistics[names]["AveCost"] = statMin[0]
            statistics[names]["MaxCost"] = statMin[1]
            statistics[names]["MinCost"] = statMin[2]
            statistics[names]["CostToDemandRate"] = old_div(statMin[0],demandCost)
            statistics[names]["AveWaiting"] = statMin[3]
            statistics[names]["MaxWaiting"] = statMin[4]
            statistics[names]["MinWaiting"] = statMin[5]
            statistics[names]["DeadlineMissRate"] = statMin[6]
            statistics[names]["FailureRate"] = statMin[7]
            statistics[names]["ImmediateStartRate"]=statMin[8]
            statistics[names]["NoOfFailure"]=statMin[9]
            statistics[names]["SuccessCostToDemandRate"]=old_div(statMin[10],demandCost)
            statistics[names]["SuccessTotalCostToDemandRate"]=old_div(statMin[11],demandCost)
            statistics[names]["AveRealExeTime"]=statMin[12]
        FullStatList.append(statistics)
        if continuesExe:
            filePath = SimDetailPath+"/"+i+"_"+z+"_continues"+caseStr
        else:
            filePath = SimDetailPath+"/"+i+"_"+z+caseStr
        f=open(filePath,"w")
        f.write("Statistics Information for Instance "+i+" in zone "+z+":\n")
        line="Algorithm "
        keyList=list(statistics[algNames[0]].keys())
        for j in keyList:
            line+=j+" "
        line+="\n"
        f.write(line)
        for names in algNames:
            line=names+" "
            for j in keyList:
                line+=str(statistics[names][j])+" "
            line+="\n"
            f.write(line)
        f.write("Detailed Results:\n")
        line=""
        for k in range(0,len(res_List[algNames[0]])):
            for names in algNames:
                line+=names+": "
                line+= "Cost: "+str(res_List[names][k][0])+" TotalExecution: "+ str(res_List[names][k][1])+" RealExecution: "+str(res_List[names][k][2])+" NoOfFailure: "+str(res_List[names][k][7])+" "
            line+="\n"
            
            f.write(line)
            line=""
        f.close()
        if not os.path.exists(StatFull):
            f=open(StatFull,"a")
            line="InstanceType    Zone    "
            for j in algNames:
                for k in keyList:
                    line+=j+"_"+k+"    "
            line+="\n"
            f.write(line)
        else:
            f=open(StatFull,"a")
            

        line=statistics["Instance"]+"    "+statistics["Zone"]+"    "
        for j in algNames:
            
            for k in keyList:
                line+=str(statistics[j][k])+"    "
        line+="\n"
        f.write(line)
        f.close()
        print(i+" "+z+" finished!\n")
print("Finish simulation!")
print("Start draw bar charts")

#for s in FullStatList:
#    DrawBarChart(s)
    
print("All done!")

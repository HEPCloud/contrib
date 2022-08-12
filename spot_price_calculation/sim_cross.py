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
#instances=["m3.2xlarge","c3.2xlarge","m3.medium","m3.large","m3.xlarge","c3.large","c3.xlarge","c3.4xlarge","c3.8xlarge"]
zone=["us-west-2a", "us-west-2b","us-west-2c","us-west-1a","us-west-1c","us-east-1b", "us-east-1c","us-east-1d"]
#instances=["c4.xlarge"]
#zone=["us-east-1b"]
if not int(sys.argv[3])==0:
    algNames=["MinPrice", "Min+25", "MaxPrice", "DemandPrice", "Demandx4","Demandx10", "Demandx.25", "Demandx.95","AdaptiveBid", "Adaptive+25", "AdaptiveMarket+25","OptimalBid"]
#    algNames=["Demandx.25"]
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
timstamp=datetime.datetime.utcnow()
SimDetailPath="SimulationCross/Detail-"+timstamp.strftime("%Y-%m-%d")
SimBarchartPath="Simulation/Bar"
caseStr="_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]
StatFull=timstamp.strftime("%Y-%m-%d")+"-SimulationTotalResultCrossZones"+caseStr
if not os.path.exists(SimDetailPath):
    os.mkdir(SimDetailPath)
if not os.path.exists(SimBarchartPath):
    os.mkdir(SimBarchartPath)

def DrawBarChart(statistic):
    import matplotlib.pyplot as plt
    
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


st=datetime.datetime.utcnow()    
global_min_price_per_ecu=getMinPricePerECU(instances,zone)
et=datetime.datetime.utcnow()
df=(et-st).total_seconds()
print("Getting min ecu price using: "+str(df)+" seconds!")
ABSendTime=datetime.datetime.utcnow()
startTime=ABSendTime-timedelta(days=90)
simulationLength=jobDeadline+1
endTime=startTime+timedelta(seconds=simulationLength)

priceHistory={}
for i in instances:
    for z in zone:
        try:
            priceHistory[i+z]=simulation(i,z,startTime,ABSendTime)
        except:
            continue


statistics={}
final_res_list={}
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
            try:
                sim=priceHistory[i+z]
            except:
                continue
            priceMax=sim.maxPrice()
            priceMin=sim.minPrice()
            demandPrice=std_prices[i]
            startPrice=sim.fullData[0][1]
            #startTime= sim.fullData[0][0]
            #endTime=sim.fullData[len(sim.fullData)-1][0]
#        startTime=sim.fullData[0][0]+timedelta(hours=1440)
#        endTime=startTime+timedelta(hours=200)
            #simulationLength=(endTime-startTime).total_seconds()
        
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
            if not int(sys.argv[3])==0:
                adp=adaptive_bid.bid_cheapest(i,z,sim,global_min_price_per_ecu)
                opt=adaptive_bid.optimal_bid(i,z,sim)  
            else:
                ama=Amazing(i,z,sim)   
            
            while count<2:
                try:
                    simulationLength=(endTime-startTime).total_seconds()
                    countStartTime= datetime.datetime.utcnow()
                    countEndTime=countStartTime
                    if not int(sys.argv[3])==0:
                        if not continuesExe:
                            result_min=sim.simulation(startTime, simulationLength, priceMin, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                        else:
                            result_min=SimulationDeadline(startTime, priceMin)
                        res_List["MinPrice"].append(result_min)             
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("Min: "+str(timeLap))
                            print("Bid Min: " + str(startTime)+" "+str(result_min)+"\n")
                        if not continuesExe:
                            result_min_25=sim.simulation(startTime, simulationLength, priceMin*1.25, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                        else:
                            result_min_25=SimulationDeadline(startTime, priceMin*1.25)
                        res_List["Min+25"].append(result_min_25)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()
                        if topDebug:
                            print("Min25: "+str(timeLap))
                            print("Bid Min+25%: " +str(startTime)+" "+ str(result_min_25)+"\n")         
                        if not continuesExe:
                            result_max=sim.simulation(startTime, simulationLength, priceMax, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                        else:
                            result_max=SimulationDeadline(startTime, priceMax)
                        res_List["MaxPrice"].append(result_max)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()                        
                        countEndTime=datetime.datetime.utcnow()             
                        if topDebug:
                            print("Max: "+str(timeLap))                              
                            print("Bid Max: " + str(startTime)+" "+str(result_max)+"\n")
                        if not continuesExe:
                            result_demand=sim.simulation(startTime, simulationLength, demandPrice, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                        else:
                            result_demand=SimulationDeadline(startTime, demandPrice)
                        res_List["DemandPrice"].append(result_demand)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()              
                        if topDebug:
                            print("Demand: "+str(timeLap))
                            print("Bid Demand: " + str(startTime)+" "+str(result_demand)+"\n")
                        if not continuesExe:
                            result_demandx4=sim.simulation(startTime, simulationLength, demandPrice*4, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                        else:
                            result_demandx4=SimulationDeadline(startTime, demandPrice*4)
                        res_List["Demandx4"].append(result_demandx4)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("4xDemand: "+str(timeLap))
                            print("Bid Demand x 4: " + str(startTime)+" "+str(result_demandx4)+"\n")   
                         
                        if not continuesExe:
                            result_demandx10=sim.simulation(startTime, simulationLength, demandPrice*10, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                        else:
                            result_demandx10=SimulationDeadline(startTime, demandPrice*10)
                        res_List["Demandx10"].append(result_demandx10)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("10xDemand: "+str(timeLap))
                            print("Bid Demand x 10: " + str(startTime)+" "+str(result_demandx4)+"\n")  
                         
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
 
                        if not continuesExe:
                            result_demandx95=sim.simulation(startTime, simulationLength, demandPrice*0.95, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)  
                        else:
                            result_demandx95=SimulationDeadline(startTime, demandPrice*0.95)
                        res_List["Demandx.95"].append(result_demandx95)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("0.95xDemand: "+str(timeLap))
                            print("Bid Demand x 0.95: " + str(startTime)+" "+str(result_demandx95)+"\n")  
                           
                        adpBid=adp.calculateBid(startTime)[0]
                        if not continuesExe:
                            result_adp=sim.simulation(startTime, simulationLength, adpBid, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                        else:
                            result_adp=SimulationDeadline(startTime, adpBid)
                        res_List["AdaptiveBid"].append(result_adp)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("Adp: "+str(timeLap))
                            print("Bid adaptive: " + str(startTime)+" "+str(result_adp)+"\n")
                  
                        if not continuesExe:
                            result_adp_market_25=sim.simulation(startTime, simulationLength, adp.calculateBid_market(startTime)[0]*1.25, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                        else:
                            result_adp_market_25=SimulationDeadline(startTime, adp.calculateBid_market(startTime)[0]*1.25)
                        res_List["AdaptiveMarket+25"].append(result_adp_market_25)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("AdpMarket+25: "+str(timeLap))
                            print("Bid adaptive market+25%: " + str(startTime)+" "+str(result_adp)+"\n")
                     
                        if not continuesExe:
                            result_adp25=sim.simulation(startTime, simulationLength, adpBid*1.25, jobExecution, jobDeadline, resumeOverhead, checkOverhead,startPrice, 0, True, continuesExe, debug)
                        else:
                            result_adp25=SimulationDeadline(startTime, adpBid*1.25)
                        res_List["Adaptive+25"].append(result_adp25)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()                
                        if topDebug:
                            print("Adp+25: "+str(timeLap))
                            print("Bid adaptive+25%: " + str(startTime)+" "+str(result_adp)+"\n")
                     
                        if continuesExe:
                            SimStartTime=startTime
                            resubmitFrequency=3600
                            failure=0
                            cost=0.0
                            totalExe=0.0
                            realExe=0.0
                            simDuration=jobDeadline
                            index=1
                            while  SimStartTime < startTime+datetime.timedelta(seconds=jobDeadline):             
                              
                                tmpRes=opt.simulation(SimStartTime, simDuration, jobExecution, simDuration, resumeOverhead, checkOverhead, continuesExe, debug)
                                cost+=tmpRes[0]
                                if tmpRes[2]>0:
                                    realExe=tmpRes[2]
                             
                                if index==1:
                                    immedStart=tmpRes[6]
                                index+=1
                              
                                if tmpRes[2]==0:
                                    simDuration-=resubmitFrequency
                                    SimStartTime+=datetime.timedelta(seconds=resubmitFrequency)
                                    totalExe+=resubmitFrequency
                                else:
                                    simDuration=jobDeadline - tmpRes[1]-resubmitFrequency
                                    SimStartTime = SimStartTime+datetime.timedelta(seconds=tmpRes[1]+resubmitFrequency)
                                    totalExe+=tmpRes[1]
                                    if tmpRes[2]<jobExecution:
                                        failure+=1
                                if realExe>=jobExecution:
                                    break
                            result_opt= (cost,totalExe,realExe, 0,0,0,immedStart,failure,sim.zone)
                        else:
                            result_opt=opt.simulation(startTime, jobDeadline, jobExecution, jobDeadline, resumeOverhead, checkOverhead, continuesExe, debug)
                        res_List["OptimalBid"].append(result_opt)
                        timeLap=(datetime.datetime.utcnow()-countEndTime).total_seconds()
                        countEndTime=datetime.datetime.utcnow()
                        if topDebug:
                            print("Opt: "+str(timeLap))
                            print("Bid optimal: " + str(startTime)+" "+str(result_opt)+"\n")
                    else:
                        if continuesExe:
                            SimStartTime=startTime
                            resubmitFrequency=3600
                            failure=0
                            cost=0.0
                            totalExe=0.0
                            realExe=0.0
                            simDuration=jobDeadline
                            index=1
                            while  SimStartTime<startTime+datetime.timedelta(seconds=jobDeadline):
                 
                             
                                tmpRes=ama.simulation(SimStartTime, simDuration, jobExecution, simDuration, resumeOverhead, checkOverhead, continuesExe, debug)
                                cost+=tmpRes[0]
                                totalExe+=tmpRes[1]+resubmitFrequency
                                if tmpRes[2]>0:
                                    realExe=tmpRes[2]
                                if tmpRes[2]<jobExecution:
                                    failure+=1
                                if index==1:
                                    immedStart=tmpRes[6]
                                index+=1
                                if realExe>=jobExecution:
                                    break
                                simDuration=jobDeadline - tmpRes[1]-resubmitFrequency
                                SimStartTime = SimStartTime+datetime.timedelta(seconds=tmpRes[1]+resubmitFrequency)
                            result_ama= (cost,totalExe,realExe, 0,0,0,immedStart,failure,sim.zone)
                        else:
                            result_ama=ama.simulation(startTime, jobDeadline, jobExecution, jobDeadline, resumeOverhead, checkOverhead, continuesExe, debug)
                        res_List["AmazingBid"].append(result_ama)
                        if topDebug:
                            print("Bid amazing: " + str(startTime)+" "+ str(result_ama)+"\n")
                    
                    countEndTime=datetime.datetime.utcnow()
                    timeLap=(countEndTime-countStartTime).total_seconds()
                
                    print(i+" in "+ z + " finished, using: "+str(timeLap))
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
        #FullStatList.append(statistics)
#     if continuesExe:
#         filePath = SimDetailPath+"/"+i+"_continues"+caseStr
#     else:
#         filePath = SimDetailPath+"/"+i+caseStr
#     f=open(filePath,"w")
#     f.write("Statistics Information for Instance "+i+":\n")
#     line="Algorithm "
    keyList=list(statistics[i][algNames[0]].keys())
#     for j in keyList:
#         line+=j+" "
#     line+="\n"
#     f.write(line)
#     for names in algNames:
#         line=names+" "
#         for j in keyList:
#             line+=str(statistics[i][names][j])+" "
#             line+="\n"
#         f.write(line)
#     f.write("Detailed Results:\n")
#     line=""
#     #f.write(line)
#     for k in range(0,len(final_res_list[i][algNames[0]])):
#         for names in algNames:
#             line+=names+": "
#             line+= "Cost: "+str(final_res_list[i][names][k][0])+" TotalExecution: "+ str(final_res_list[i][names][k][1])+" RealExecution: "+str(final_res_list[i][names][k][2])+" NoOfFailure: "+str(final_res_list[i][names][k][7])+" Zone: "+str(final_res_list[i][names][8])+" "
#         line+="\n"
#             
#         f.write(line)
#         line=""
#     f.close()
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

for s in FullStatList:
    DrawBarChart(s)
    
print("All done!")

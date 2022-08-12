from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
import datetime
import numpy
import os.path
from SpotPriceHistory import *


class simulation(object):
    #priceList=list()
    #fullData=dict()
    instanceType=""
    zone=""
    totalSeconds=0
    
    def __init__(self,instanceType,zone,start=None, end=None):
        self.instanceType=instanceType

        print("setting zone...\n")
        self.zone=zone

        print("receiving price list...\n")
        self.priceList=list()

        print("receiving full data...\n")
        self.fullData=list()

        print("setting histogram...\n")
        self.histogram=dict()

        print("reading database...\n")
        self.readData(start,end)

        print("sorting histogram...\n")
        self.sortHistogram()
    
    def sortHistogram(self):
        self.sortedList=[]
        for k in sorted(self.histogram.keys()):
            self.sortedList.append((k,self.histogram[k],old_div(self.histogram[k],self.totalSeconds)))
            
    def readData(self,start=None,end=None):
        filename="Database/"+self.instanceType+"_"+self.zone
        #print filename
        if not os.path.isfile(filename):
            print("File does not exit!")
        else:
            with open(filename,"r") as f:
                content=f.read().splitlines()
                       
            tempStr=content[1].split(" ")
            preDate=datetime.datetime.strptime(tempStr[0],"%Y-%m-%dT%H:%M:%S.%f")
            lastDate=datetime.datetime.strptime(content[len(content)-1].split(" ")[0],"%Y-%m-%dT%H:%M:%S.%f")
            if start==None:
                start=preDate
            if end==None:
                end=lastDate
            self.totalSeconds=(end-start).total_seconds()
            prePrice=-1
            first=False
            for i in range(1,len(content)):
                tempStr=content[i].split(" ")
                date=datetime.datetime.strptime(tempStr[0],"%Y-%m-%dT%H:%M:%S.%f")
                price=float(tempStr[1])
                if date<start or date>end:
                    preDate=date
                    continue
                
                if not first:
                    first=True
                    self.fullData.append((date,price))
                    preDate=date
                    prePrice=price
                    continue
                
                if not price==prePrice:
                    self.fullData.append((date,price))
                duration=date-preDate
                if not prePrice in self.histogram:
                    self.histogram[prePrice]=duration.total_seconds()
                else:
                    self.histogram[prePrice]+=duration.total_seconds()
                preDate=date
                prePrice=price
                date=tempStr[0]
                #print i
#                 if not date in self.fullData:
#                     self.fullData[date]=tempStr[1]
#                 self.priceList.append(numpy.double(tempStr[1]))
            f.close()
           # print self.instanceType+" "+ self.zone+" "+str(len(content)-len(self.fullData))
        
    def findIndex(self,date):
        start=0
        end=len(self.fullData)
        middle=old_div(end,2)
        while middle!=start or middle!=end or middle != len(self.fullData)  or middle !=0:
            if date >= self.fullData[len(self.fullData)-1][0]:
                return len(self.fullData)-1
            if date <= self.fullData[0][0]:
                return 0
            if date>= self.fullData[middle][0] and date <= self.fullData[middle+1][0]:
                return middle
            if date>=self.fullData[middle-1][0] and date <= self.fullData[middle][0]:
                return middle-1
            if date >= self.fullData[middle+1][0]:
                start=middle+1
                middle=start+old_div((end-start),2)
            else:
                end=middle-1
                middle=start+old_div((end-start),2) 
            
        
    def findPrice(self, date):
        return self.fullData[self.findIndex(date)][1]
    
    def priceChangeRate(self, t, duration):
        start=t-datetime.timedelta(seconds=duration)
        return old_div(duration,(1 if self.findIndex(t)==self.findIndex(start) else self.findIndex(t)-self.findIndex(start)))
    
    def sim_bid(self,bid, startTime):
        index=self.findIndex(startTime)
        price=self.fullData[index][1]
        endTime=startTime
        while price <= bid and endTime <= self.fullData[len(self.fullData)-1][0] and index < len(self.fullData):
            endTime=self.fullData[index][0]
            price=self.fullData[index][1]
            index+=1
        nextTime= endTime+datetime.timedelta(seconds=3600) if endTime< self.fullData[len(self.fullData)-1][0] else endTime
        duration=endTime-startTime
        return (old_div(duration.total_seconds(),(24.00*3600)), nextTime)
    
    def constructSubDataList(self,index, startTime, index_end, endTime):
        #index_start=self.findIndex(startTime)
        #index_end=self.findIndex(endTime)
        newList=[]
#         if startTime == endTime :
#             newList.append((startTime,self.fullData[index_start][1]))
#             newList.append((endTime,self.fullData[index_end][1]))
#         else:
#             newList.append((startTime,self.fullData[index_start][1]))
          
        for i in range(0,index_end):
            newList.append(self.fullData[i])
            if i==index and not startTime==self.fullData[index][0]:
                newList.append((startTime,self.fullData[i][1]))
        if index==index_end:
            newList.append((startTime,self.fullData[index][1])) 
        if endTime<self.fullData[len(self.fullData)-1][0]:
            newList.append((endTime,self.fullData[index_end][1]))
        return newList
                
    
    def simulation(self, bid_time, simDuration, bid_price, executionDemand, deadline, overheadResume, overheadCheckpoint, lastPrice, remainSeconds=0, ifCheckPointing=False, ifContinue=True, ifDebug=False):
        '''
        This function calculates the total price and execution time on executing a given job on spot instance
        bid_time: (datetime), the time instance to bid
        simDuration: (seconds) the time simulation runs
        bid_price: (float), the bid price
        executionDemand: (seconds), the execution demand of the given job
        deadline: (seconds), the deadline of the given job
        overheadResume: (seconds) the time to restart an instance
        overheadCheckpoint: (seconds) the time to checkpointing
        lastPrice: (float)  price of running instance in last integral hour
        remainSeconds: (int) remaining seconds form last integral hour
        ifCheckPointing: (boolean), if check pointed as last hour
        ifContinue: (boolean), if the simulation only count on continue execution or can be interrupt and recovery
        ifDebug: (boolean), if show debug information
        return type: (totalCost, totalExecutionTime, realExecutionTime, num_of_checkpoint, lastPrice, remainSeconds, immediateStart,noOfFailue) 
        
        '''
        print("simulation started!")
        #countStartIn=datetime.datetime.utcnow()
        index=self.findIndex(bid_time)
        preempty=False
        bidEndTime=bid_time+datetime.timedelta(seconds=simDuration)
        end_index=self.findIndex(bidEndTime)
        fullData=self.constructSubDataList(index,bid_time,end_index,bidEndTime )
        #print len(fullData)
        totalCost=0.
        totalExecutionTime=0
        realExecutionTime=0
        executionTime=0
        num_of_checkpoint=0
        remainExe=executionDemand
        remainSeconds=0
        lastTime=bid_time
        checkpointing=ifCheckPointing
        currentPrice = lastPrice
        index+=1
        immediateStart=False
#         if self.fullData[index][1]>bid_price and ifContinue==True and preempty:
#             if ifDebug:
#                 print ("[DEBUG S-1:] VM instance will not be started!")
#             return (totalCost, totalExecutionTime, realExecutionTime,num_of_checkpoint,lastPrice, remainSeconds)
#         countStart=datetime.datetime.utcnow()
#         loopCount=1
        while remainExe>0 and index < len(fullData):
            marketPrice=fullData[index][1]
            if marketPrice<=bid_price:
                if totalExecutionTime==0:
                    immediateStart=True
                diff = (fullData[index][0]-lastTime).total_seconds()
                if diff==0:
                    index+=1
                elif diff>= remainExe+overheadResume and checkpointing:
                    
                    if diff - remainExe - overheadResume < 3600 and fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                        totalCost+=numpy.floor(old_div(remainExe,3600))*fullData[index][1]
                    else:
                        totalCost+=numpy.ceil(old_div(remainExe,3600))*fullData[index][1]                        
                    realExecutionTime+=remainExe 
                    totalExecutionTime+=remainExe
                    if ifDebug:
                        print ("[DEBUG S-2:] Execution from: "+str(lastTime)+" to "+str(lastTime+datetime.timedelta(seconds=remainExe))+", Execution Time: "+ str(remainExe)+" seconds, realExecution: "+str(realExecutionTime)+" seconds, TotalExecution: "+str(totalExecutionTime) +" seconds, TotalCost: "+ str(totalCost)+" Remaining: 0 seconds\n")
                    remainExe=0
                    currentPrice=fullData[index][1]
                    index+=1
                elif diff< remainExe+overheadResume and diff >= remainExe and checkpointing:
                    if diff - remainExe - overheadResume < 3600 and fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                        totalCost+=numpy.floor(old_div(remainExe,3600))*fullData[index][1]
                        checkpointing=True
                        exeTime=diff - overheadResume - overheadCheckpoint
                        realExecutionTime+=exeTime 
                        remainExe=remainExe-diff + overheadResume+overheadCheckpoint
                    else:
                        totalCost+=numpy.ceil(old_div(remainExe,3600))*fullData[index][1] 
                        checkpointing=False  
                        exeTime=diff - overheadResume 
                        realExecutionTime+=exeTime     
                        remainExe=remainExe - diff + overheadResume
                    totalExecutionTime+=diff
                    if ifDebug:
                        print ("[DEBUG S-2-1:] Execution from: "+str(lastTime)+" to "+str(lastTime+datetime.timedelta(seconds=remainExe))+", Execution Time: "+ str(exeTime)+" seconds, realExecution: "+str(realExecutionTime)+" seconds, TotalExecution: "+str(totalExecutionTime) +" seconds, TotalCost: "+ str(totalCost)+" Remaining: 0 seconds\n")
                    
                    currentPrice=fullData[index][1]
                    index+=1
                elif diff>=remainExe - remainSeconds and not checkpointing:
                    if remainSeconds >= 0:
                        if remainExe >= 3600:
                            totalCost += currentPrice                        
                            remain=remainExe - 3600
                            if diff - remainExe + remainSeconds  < 3600 and fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                                totalCost+=numpy.floor(old_div(remain,3600))*fullData[index][1]
                            else:
                                totalCost+=numpy.ceil(old_div(remain,3600))*fullData[index][1]  
                        else:
                            if diff + remainSeconds < 3600 and fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                                totalCost+=0
                            else:
                                totalCost+=currentPrice  
                    realExecutionTime+=remainExe 
                    totalExecutionTime+=remainExe - remainSeconds
                    if ifDebug:
                        print ("[DEBUG S-3:] Execution from: "+str(lastTime)+" to "+str(lastTime+datetime.timedelta(seconds=remainExe))+", Execution Time: "+ str(remainExe)+" seconds, realExecution: "+str(realExecutionTime)+" seconds, TotalExecution: "+str(totalExecutionTime) +" seconds, TotalCost: "+ str(totalCost)+" Remaining: 0 seconds\n")
 
                    remainExe=0
                    
                    currentPrice=fullData[index][1]
                    index+=1
                elif diff < remainExe and checkpointing:
                    currentPrice = fullData[index][1]
                    totalCost+=numpy.floor(old_div(diff,3600))*fullData[index][1]
                    
                    if fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                        checkpointing = True
                        num_of_checkpoint+=1
                        exe = max([0,diff - overheadResume - overheadCheckpoint])   
                        remainSeconds=0            
                        totalExecutionTime+=diff
                        remainExe = remainExe - exe
                        realExecutionTime +=  exe 
                        if not realExecutionTime==0:
                            preempty=True
                    else:
                        checkpointing = False
                        if diff>=3600:
                            exe=numpy.floor(old_div(diff,3600)) * 3600
                        else:
                            exe=0
                        #exe = max([0,diff - overheadResume])
                        
                        remainSeconds = diff - numpy.floor(old_div(diff,3600)) * 3600
                        totalExecutionTime+=diff
                        remainExe = remainExe - exe
                        realExecutionTime +=  exe 
                    if ifDebug:
                        print ("[DEBUG S-4:] Execution from: "+str(lastTime)+" to "+str(lastTime+datetime.timedelta(seconds=diff))+", Execution Time: "+ str(exe)+" seconds, realExecution: "+str(realExecutionTime)+" seconds, TotalExecution: "+str(totalExecutionTime) +" seconds, TotalCost: "+ str(totalCost)+" Remaining: "+str(remainExe)+" seconds\n")
 
                    lastTime=fullData[index][0]
                    index+=1
                elif diff < remainExe and not checkpointing:
                    if diff + remainSeconds < 3600:
                        if fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                            checkpointing = True
                            num_of_checkpoint+=1
                            exe =max([0, diff + remainSeconds - overheadCheckpoint])
                            realExecutionTime+=exe
                            remainSeconds=0
                            currentPrice=0
                            preempty=True
                        else:
                            checkpointing=False
                            remainSeconds+=diff
                            exe=0
                    else:
                        totalCost+=currentPrice
                        remain = diff+remainSeconds-3600
                        if fullData[index+1 if index+1< len(fullData)-1 else index][1] > bid_price:
                            checkpointing=True
                            totalCost+=numpy.floor(old_div(remain,3600))*fullData[index][1]
                            exe = remainSeconds + diff - overheadCheckpoint                            
                            realExecutionTime+=exe
                            remainExe-=exe
                            remainSeconds=0
                            currentPrice=0
                            num_of_checkpoint+=1
                            preempty=True
                        else:
                            checkpointing=False
                            currentPrice = fullData[index][1]
                            if remain < 3600:
                                remainSeconds = remain 
                                exe = 3600                               
                            else:
                                totalCost+=numpy.floor(old_div(remain,3600))*currentPrice 
                                remainSeconds = remain - numpy.floor(old_div(remain,3600))*3600
                                exe= 3600 + numpy.floor(old_div(remain,3600))*3600
                            remainExe = remainExe - exe
                            realExecutionTime+=exe
                    totalExecutionTime+=diff
                        
                    #realExecutionTime += exe 
                    if ifDebug:
                        print ("[DEBUG S-5:] Execution from: "+str(lastTime)+" to "+str(lastTime+datetime.timedelta(seconds=diff))+", Execution Time: "+ str(exe)+" seconds, realExecution: "+str(realExecutionTime)+" seconds, TotalExecution: "+str(totalExecutionTime) +" seconds, TotalCost: "+ str(totalCost)+" Remaining: "+str(remainExe)+" seconds\n")
  
                    lastTime=fullData[index][0]
                    index+=1 
                
            else:
                totalExecutionTime += (fullData[index][0]-lastTime).total_seconds()
                checkpointing = True
                if not realExecutionTime==0:
                    preempty=True
                if ifDebug:
                    print ("[DEBUG S-6:] Execution from: "+str(lastTime)+" to "+str(fullData[index][0])+", Execution Time: 0 seconds, realExecution: "+str(realExecutionTime)+" seconds, TotalExecution: "+str(totalExecutionTime) +" seconds, TotalCost: "+ str(totalCost)+" Remaining: "+str(remainExe)+" seconds\n")
 
                lastTime=fullData[index][0]
                index+=1
            if preempty and ifContinue:
                break
#             loopCount+=1
#         countEnd=datetime.datetime.utcnow()
#         diffCount=(countEnd-countStart).total_seconds()
#         diffTotal=(countEnd-countStartIn).total_seconds()
#         print loopCount
#         print diffCount
#         print diffTotal
        return (totalCost, totalExecutionTime, realExecutionTime, num_of_checkpoint, currentPrice, remainSeconds,immediateStart,0)
    
    def dump(self):
        #self.readData()
        for i in self.fullData:
            print(i)
#         for i in sorted(self.priceList):
#             print i
#         print "max: " + str(self.maxPrice())
#         print "min: " + str(self.minPrice())
#         print "Mean: " + str(self.averagePrice())
#         print "STD: " + str(self.stdPrice())
            
        
    def averagePrice(self):
        sum=0
        totalTime=0
        for i,j in self.histogram.items():
            totalTime+=j
            sum+=float(i)*j
        print("avg Price!")
        return old_div(sum,totalTime)
    
    def maxPrice(self):
        print("max Price!")
        return max(self.histogram.keys())
    
    def minPrice(self):
        print("min Price!")
        return min(self.histogram.keys())
    
    def stdPrice(self):
        print("std Price!")
        return numpy.std(self.histogram.keys())
    
    def pdf(self,price):
        print("pdf calculation!")
        
        for i in range(0,len(self.sortedList)-1):
            if price == self.sortedList[i][0]:
                return self.sortedList[i][2]
            elif price < self.sortedList[i][0]:
                return self.sortedList[i][2]
            elif i == len(self.sortedList)-1:
                return self.sortedList[i][2]
            elif self.sortedList[i][0]<price and price <self.sortedList[i+1][0]:
                return self.sortedList[i][2] if price-self.sortedList[i][0] <= self.sortedList[i+1][0]-price else self.sortedList[i+1][2]
            else:
                continue
            
    def cdf(self,price):
        print("cdf running!\n")
        cp=0
        for i in range(0, len(self.sortedList)-1):
            if self.sortedList[i][0]<=price:
                cp+=self.sortedList[i][2]
            else:
                break
        return cp
    
    def expect(self,price):
        print("expect calculation running!\n")
        cp=0.0
        index=0
        for i in range(0, len(self.sortedList)):
            if self.sortedList[i][0]<=price:
                cp+=self.sortedList[i][2]
                index=i
            else:
                break
        n=(self.sortedList[index][0]-self.sortedList[0][0])*10000
        return old_div(cp,n) if n>0 else cp            
                       
    def writeLog(self,filename):
        print("writing log!\n")
        if not os.path.isfile(filename):
            f=open(filename,"w")
            f.write("InstanceType Zone Average Max Min\n")
            f.write(self.instanceType + " "+self.zone+" "+ str(self.averagePrice())+" "+
                    str(self.maxPrice())+" "+str(self.minPrice())+"\n")
            f.close()
        else:
            f=open(filename,"a")
            f.write(self.instanceType + " "+self.zone+" "+ str(self.averagePrice())+" "+
                    str(self.maxPrice())+" "+str(self.minPrice())+"\n")
            f.close()
    
    def writeHistogram(self):
        print("writing histogram!\n")
        filename="Histogram/"+self.instanceType+"_"+self.zone
        if os.path.isfile(filename):
            os.remove(filename)
        f=open(filename,"w")
        f.write("Price Duration(Seconds) Distribution\n")
        for i,j in sorted(self.histogram.items()):
            f.write(str(i)+" "+str(j)+" "+str(float(j)/self.totalSeconds)+"\n")
        f.close()
        
    def plotHistogram(self):
        import matplotlib.pyplot as plt
        print("plotting histogram!")
#        fig=plt.figure()
#        ax=fig.add_subplot(111)
        y=[]
        for i in sorted(self.histogram.keys()):
            y.append(float(self.histogram[i])/self.totalSeconds)
        
        ind=numpy.arange(len(self.histogram))
        width=0.8
        plt.bar(ind, y, width, color='r')
        x=[]
        x_labels=[]
        num_of_ticks=5
        for i in range(0,num_of_ticks):
            index=old_div(len(self.histogram),num_of_ticks)*i
            x.append(index)
            x_labels.append(sorted(self.histogram.keys())[index])
        x.append(len(self.histogram)-1)
        x_labels.append(sorted(self.histogram.keys())[len(self.histogram)-1])
            
        plt.xticks(x,x_labels)
        plt.title(self.instanceType+"-"+self.zone)
#        ax.set_title(self.instanceType+"-"+self.zone)
        
        #xTickMarks = sorted(self.histogram.keys())
        #xtickNames=ax.set_xticklabels(xTickMarks)
        #ax.xticks(len(self.histogram),sorted(self.histogram.keys()))
        #ax.set_xticklabels(sorted(self.histogram))
        #plt.setp(xtickNames, rotation=90, fontsize=5)
#        ax.bar(range(len(y)),y)
 #       ax.xaxis.set_ticks(x,x)
     #   plt.show()
        plt.savefig("Histogram/"+self.instanceType+"_"+self.zone+".png")
        plt.close()
        
def getMinPricePerECU(instances, zones):
    minPricePerECU=float('inf')
    for i in instances:
        for z in zones: 
            try:
                sim=simulation(i,z)
                ecu_price=old_div(sim.minPrice(),ecu[i])
                if ecu_price<=minPricePerECU:
                    minPricePerECU=ecu_price
            except:
                continue
    print("min price calculation %d\n" % minPricePerECU)
    return minPricePerECU
            

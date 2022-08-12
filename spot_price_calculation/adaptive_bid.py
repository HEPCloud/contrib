'''
Created on Jul 14, 2015

@author: hao
'''
from __future__ import division
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
from analysis import simulation
import numpy
import SpotPriceHistory
from numpy import average
from datetime import datetime, timedelta

class bid_cheapest(object):
    '''
    classdocs
    '''
    global_min_price_per_ecu_h = 0.00229

    def __init__(self,instanceType, zone, sim, global_min_price_per_ecu_h):
        '''
        Constructor
        '''
        self.bidHistory=list()
        self.instanceType=instanceType
        self.zone=zone
        self.his_data=sim
        self.sim_results=list()
        self.global_min_price_per_ecu_h=global_min_price_per_ecu_h
    def calculateBid(self,startDate):
        price=self.his_data.findPrice(startDate)
        f=self.his_data.priceChangeRate(startDate, 6*3600)*5*60
        for ref_accept10 in range(10,21):
            ref_accept = ref_accept10/10.0            
            if old_div(price,SpotPriceHistory.ecu[self.instanceType]) <= self.global_min_price_per_ecu_h*ref_accept:
                bid = old_div(int((price+0.00010001)*1E4),1E4)
                return (bid,f)
        return (self.global_min_price_per_ecu_h*SpotPriceHistory.ecu[self.instanceType], f)
    
    def calculateBid_market(self,startDate):
        price=self.his_data.findPrice(startDate)
        f=self.his_data.priceChangeRate(startDate, 6*3600)*5*60
        return (old_div(int((price+0.00010001)*1E4),1E4), f)
        
    def simulation(self):
        startTime=self.his_data.fullData[0][0]
        lastTime=self.his_data.fullData[len(self.his_data.fullData)-1][0]
        while startTime < lastTime:
            bid = self.calculateBid(startTime)
            results=self.his_data.sim_bid(bid[0], startTime)
            self.sim_results.append((startTime, bid[0], results[0], bid[1]))
            startTime = results[1]
        
        overhead = 1.0
        success=0.0
        liveTime=list()
        for i in self.sim_results:
            liveTime.append(i[2])
            if overhead < i[2]:
                success+=1
         
        filename="Simulation/"+self.instanceType+"_"+self.zone+"_adp"
        f=open(filename,"w")
        f.write("Success_Rate Ave_Duration Max_Duration Min_Duration\n")
        f.write(str(old_div(success,len(liveTime)))+" "+str(average(liveTime))+" "+str(max(liveTime))+" "+str(min(liveTime))+"\n")
        f.write("Bid_Time Bid_price Duration Checkpoint_F\n")
        for i in self.sim_results:
            f.write(str(i[0])+" "+str(i[1])+" "+str(i[2])+" "+str(i[3])+"\n")
        f.close()
        
class optimal_bid(object):
    
    p=0.5
#    deadline=10
    
    def __init__(self, instanceType, zone, sim):
        self.bidHistory=list()
        self.instanceType=instanceType
        self.zone=zone
        self.his_data=sim
        self.sim_results=list()
    
    def calculateBid(self,price,deadline):
        '''
        deadline in hours, int
        '''
        cdf=self.his_data.cdf(price)
        g=self.his_data.expect(price)
        new_price = price-(1-self.p)*cdf*(price-g)
        if deadline>1:
            return self.calculateBid(new_price, deadline-1)
        else:
            return new_price
        
    def simulation_old(self, execution, deadline):
        '''
        both execution and deadline are in hours
        '''
        success=0.0
        overhead = 60.00 / (24*3600)
        startTime=self.his_data.fullData[0][0]
        lastTime=self.his_data.fullData[len(self.his_data.fullData)-1][0]
        minPrice=self.his_data.minPrice()
        num_of_jobs = 0
        while startTime <= lastTime-timedelta(hours=deadline):
            e_j=float(execution)
            d_j=deadline
            for i in range(0,deadline):
                if int(e_j)==d_j:
                    bid=SpotPriceHistory.std_prices[self.instanceType]
                else:
                    tmp_bid=self.calculateBid(SpotPriceHistory.std_prices[self.instanceType],d_j)
                    bid=tmp_bid if tmp_bid>=minPrice else minPrice
                results=self.his_data.sim_bid(bid, startTime)
                if results[0] >= 1.0/24.0:
                    e_j-=1
                elif results[0]>=overhead and results[0]<old_div(1,24):
                    e_j=e_j-results[0]
                d_j-=1
                self.sim_results.append((startTime, bid, results[0], e_j, d_j, deadline))
                startTime=startTime+timedelta(hours=1)
                if e_j<=0:
                    success+=1
                    break;
            num_of_jobs+=1
                    
#         while startTime < lastTime:
#             bid = self.calculateBid(SpotPriceHistory.std_prices[self.instanceType],self.deadline)
#             results=self.his_data.sim_bid(bid, startTime)
#             self.sim_results.append((startTime, bid, results[0], self.deadline))
#             startTime = results[1]
#         
#         overhead = 60.00 / (24*3600)
#         success=0.0
        liveTime=list()
        for i in self.sim_results:
            liveTime.append(i[2])
#             if overhead < i[2]:
#                 success+=1
#          
        filename="Simulation/"+self.instanceType+"_"+self.zone+"_opt"
        f=open(filename,"w")
        f.write("Success_Rate Ave_Duration Max_Duration Min_Duration Job_deadline Total_Run\n")
        f.write(str(old_div(success,num_of_jobs))+" "+str(average(liveTime))+" "+str(max(liveTime))+" "+str(min(liveTime))+" "+str(deadline)+" "+str(num_of_jobs)+"\n")
        f.write("Bid_Time Bid_price Duration Remain_Exe Deadline\n")
        for i in self.sim_results:
            f.write(str(i[0])+" "+str(i[1])+" "+str(i[2])+" "+str(i[3])+" "+str(i[4])+"\n")
        f.close()
    
    def simulation(self, startTime, simLength, execution, deadline, overheadResume, overheadCheckpoint,ifContinues,ifDebug):
        start=startTime
        totalCost=0.
        totalExe=0
        realExe=0
        num_of_Checkpoints=0
        remainExe=execution
        remainDeadline=deadline
        currentPrice=self.his_data.fullData[self.his_data.findIndex(start)][1]
        remainSeconds=0
        ifCheckPoint=True
        lastBidSuccess=False
        index=1
        firstBidSuccess=False
        while remainDeadline > 0:
            if remainExe >= remainDeadline:
                totalCost+=numpy.ceil(old_div(remainExe,3600))*SpotPriceHistory.std_prices[self.instanceType]
                totalExe+=remainDeadline
                realExe+=remainDeadline
                remainDeadline=0
            else:
                countStart=datetime.utcnow()
                bid=self.calculateBid(SpotPriceHistory.std_prices[self.instanceType],int(old_div(remainDeadline,3600)))
                bid=min([bid,self.his_data.minPrice()])   
                countEnd=datetime.utcnow()  
                if ifContinues:
                    #simLength=(self.his_data.fullData[len(self.his_data.fullData)-1][0]-start).total_seconds()     
                    countEnd=datetime.utcnow() 
                    result = self.his_data.simulation(start, simLength, bid, remainExe, remainDeadline, overheadResume, overheadCheckpoint, currentPrice, remainSeconds,ifCheckPoint, ifContinues, ifDebug)
                    countEndRes=datetime.utcnow()
                    diffBid=(countEnd-countStart).total_seconds()
                    diffRes=(countEndRes-countEnd).total_seconds()
                    #print "Cal_bid: " + str(diffBid)+" Cal_res: "+str(diffRes)
                    return result
                else:
                    result = self.his_data.simulation(start, 3600, bid, remainExe, remainDeadline, overheadResume, overheadCheckpoint, currentPrice, remainSeconds,ifCheckPoint, ifContinues, ifDebug)
                countEndRes=datetime.utcnow()
                if lastBidSuccess and result[2]==0:
                    ifCheckPoint=True
                elif lastBidSuccess and bid>0:
                    ifCheckPoint=False
                else:
                    ifCheckPoint=True
                currentPrice=result[4]
                remainSeconds=result[5]
                totalCost+=result[0]
                totalExe+=result[1]
                realExe+=result[2]
                num_of_Checkpoints+=result[3]
                start=start+timedelta(seconds=3600)
                remainDeadline-=3600
                if index==1:
                    firstBidSuccess=result[6]
                index+=1
                #print index
                #diffBid=(countEnd-countStart).total_seconds()
                #diffRes=(countEndRes-countEnd).total_seconds()
                #print "Cal_bid: " + str(diffBid)+" Cal_res: "+str(diffRes)
        return (totalCost, totalExe, realExe, num_of_Checkpoints,0,0,firstBidSuccess,0)
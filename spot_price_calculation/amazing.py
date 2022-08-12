'''
Created on Jul 20, 2015

@author: hao
'''
from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range
from past.utils import old_div
from builtins import object
import os.path
import random
import analysis
import re
from pulp import *
from datetime import timedelta

class state(object):
    in_bid=1
    out_bid=0
    
class bid(object):
    G=1
    B=0
    
class Amazing(object):
    '''
    classdocs
    '''
    t_c=300
    t_r=600


    def __init__(self, instanceType, zone, sim):
        '''
        Constructor
        '''
        self.instanceType=instanceType
        self.zone=zone
        self.pMatrix={}
        self.stateSet=[]
        self.maxPrice=0
        self.sim=sim
        self.get_pMatrix()
        self.getPriceHistory()
        self.constructStateSet(state.out_bid)
        
    def get_pMatrix(self):
        filename="Database/"+self.instanceType+"_"+self.zone
        if not os.path.isfile(filename):
            print("File does not exit!")
            exit()
        else:
            with open(filename,"r") as f:
                content=f.read().splitlines()
            tmp=content[1].split(" ")
            prePrice=float(tmp[1])
            for i in range(2,len(content)):
                tmp=content[i].split(" ")
                price=float(tmp[1])
                if prePrice in self.pMatrix:
                    if price in self.pMatrix[prePrice]:
                        self.pMatrix[prePrice][price]+=1.
                    else:
                        self.pMatrix[prePrice][price]=1.
                else:
                    self.pMatrix[prePrice]={price:1.}
                prePrice=price
            totalChanges=len(content)-1    
            for i in list(self.pMatrix.keys()):
                for j in list(self.pMatrix[i].keys()):
                    self.pMatrix[i][j]=old_div(self.pMatrix[i][j],totalChanges)
    
    def execution_prograss(self, previousState, currentState, bidOption):
        if previousState==state.in_bid and currentState==state.in_bid and bidOption==bid.G:
            return 1-self.t_c
        elif previousState==state.out_bid and currentState==state.in_bid and bidOption==bid.B:
            return 1-self.t_r
        elif previousState==state.out_bid and currentState==state.in_bid and bidOption==bid.G:
            return 1-self.t_c-self.t_r
        elif previousState==state.in_bid and currentState==state.in_bid and bidOption==bid.B:
            return 1
        else:
            return 0
        
    
    
    def dump(self):
        for i in list(self.pMatrix.keys()):
            for j in list(self.pMatrix[i].keys()):
                print(str(i)+"-->"+str(j)+":"+str(self.pMatrix[i][j]))   
    
    def getPriceHistory(self):       
        filename = "Database/"+self.instanceType+"_"+self.zone
        if not os.path.isfile(filename):
            print(filename+" does not exit!")
            exit()
        else:
            f=open(filename,"r")
            content=f.read().splitlines()
            priceList={}
            for line in range(1,len(content)):
                tempStr=content[line].split(" ")
                priceList[float(tempStr[1])]=0
            self.maxPrice=sorted(priceList.keys())[len(priceList)-1]
            return sorted(priceList.keys()) 
    
    def constructStateSet(self, previousState=state.out_bid):
        for i in self.getPriceHistory():
            self.stateSet.append((state.out_bid,state.out_bid,bid.B,i))
            self.stateSet.append((state.out_bid,state.in_bid,bid.B,i))
            self.stateSet.append((state.out_bid,state.out_bid,bid.G,i))
            self.stateSet.append((state.out_bid,state.in_bid,bid.G,i))
            self.stateSet.append((state.in_bid,state.out_bid,bid.B,i))
            self.stateSet.append((state.in_bid,state.in_bid,bid.B,i))
            self.stateSet.append((state.in_bid,state.out_bid,bid.G,i))
            self.stateSet.append((state.in_bid,state.in_bid,bid.G,i))
            
    def vlidState(self, preState, preBid, currentState, nextState):
        if not preState==currentState:
            return False
        elif preBid==bid.G and nextState==state.in_bid:
            return False
        else:
            return True
        
    def calculateMu(self, previousState,workload, deadline):
        
        prob=LpProblem("The Cost Minimization Problem", LpMinimize)
        # Define the variables for occupation measure
        vars = LpVariable.dicts("O_Measure",self.stateSet,0)
        
        # Define the objective Function
        prob += lpSum([vars[i]*i[2]*deadline for i in self.stateSet])
        
        # Define constraints
#        prob += [vars[i]>=0 for i in self.stateSet]
        prob += lpSum([vars[i] * self.execution_prograss(i[0], i[1],i[2]) for i in self.stateSet])
        prob += lpSum([vars[i] for i in self.stateSet]) == 1
        prob += lpSum([vars[i]*self.lastConstraint(i[0], i[1],i[2],i[3]) for i in self.stateSet]) == 0
        prob.writeLP("test.lp")
        prob.solve()
        return prob.variables()
#         print("Status:", LpStatus[prob.status])
#         for v in prob.variables():
#             print str(v)+"\n" 
            
    def delta(self,preState_1, currentState_1, price_1, preState_2, currentState_2, price_2):
        if preState_1==preState_2 and currentState_1==currentState_2 and price_1==price_2:
            return 1
        else:
            return 0
    
    def stateTransMatrix(self, preState, preBid, prePrice, currentState, nextState, currentPrice):
        if self.vlidState(preState, preBid, currentState, nextState):
            return self.pMatrix[prePrice][currentPrice] if prePrice in self.pMatrix and currentPrice in self.pMatrix[prePrice] else 0
        else:
            return 0
        
    def lastConstraint(self, preState, currentState, bid, price):
        totalSum=0.
        for i in self.stateSet:
            totalSum+=(self.delta(preState, currentState, price, i[0],i[1],i[3]) - self.stateTransMatrix(currentState, bid, price, i[0],i[1],i[3]))
        return totalSum
    
    def calculateBid(self, preState, exe,deadline):
        try:
            mu=self.calculateMu(preState, exe, deadline)
            index=random.randint(0,len(mu))
            tmp=re.split('[_,()]',mu[index].name)
         
            if int(tmp[3]) == bid.B:
                return self.maxPrice
            else:
                return 0
        except:
            print("Cannot find solution, give up!")
            return 0
        
    def simulation(self, startTime, simLength, execution, deadline, overheadResume, overheadCheckpoint, ifContinues, ifDebug):
        preState=state.out_bid
        remainExe=execution
        remainDeadline=deadline
        self.t_c=overheadCheckpoint
        self.t_r=overheadResume
        start=startTime
        totalCost=0.
        totalExe=0
        realExe=0
        num_of_checkpoints=0
        ifCheckPoint=True
        currentPrice=self.sim.fullData[self.sim.findIndex(start)][1]
        remainSeconds=0
        index=1
        firstBidSuccess=False
        while remainDeadline > 0:
            bid=self.calculateBid(preState, remainExe, remainDeadline)
            if preState==state.in_bid and bid==0:
                num_of_checkpoints+=1
                ifCheckPoint=True
            elif preState==state.in_bid and bid>0:
                ifCheckPoint=False
            else:
                ifCheckPoint=True
            if ifContinues and bid==0:
                return (0.,0,0,0)
            elif ifContinues and bid>0:
                #simLength=(self.sim.fullData[len(self.sim.fullData)-1][0]-start).total_seconds()
                result=self.sim.simulation(start, simLength, bid, remainExe, remainDeadline, overheadResume, overheadCheckpoint, currentPrice, remainSeconds, ifCheckPoint, ifContinues, ifDebug)
                return result
            else:   
                result=self.sim.simulation(start, 3600, bid, remainExe, remainDeadline, overheadResume, overheadCheckpoint, currentPrice, remainSeconds, ifCheckPoint, ifContinues, ifDebug)
            totalCost+=result[0]
            totalExe+=result[1]
            realExe+=result[2]
            num_of_checkpoints+=result[3]
            # Need tune the no. of checkpoints
           
            if result[2]>0:
                preState=state.in_bid
            else:
                preState=state.out_bid
            start+=timedelta(seconds=3600)
            remainDeadline-=3600
            remainExe-=result[2]
            currentPrice=result[4]
            remainSeconds=result[5]
            if index==1:
                firstBidSuccess=result[6]
            index+=1
        return (totalCost, totalExe, realExe, num_of_checkpoints,0,0, firstBidSuccess,0)
            
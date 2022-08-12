from __future__ import print_function
from __future__ import division
from builtins import str
from past.utils import old_div
import csv
import sys
import datetime

filename=sys.argv[1]
zoneConvert={
    'East-#6':'us-east-1c',
    'East-#7':'us-east-1d',
    'East-#12':'us-east-1b',
    'West-#1':'us-west-2a',
    'West-#2':'us-west-2b',
    'West-#4':'us-west-2c',
    'West-#6':'us-west-1a',
    'West-#9':'us-west-1c'
             }
'''
zoneConvert={
    'East-#6':'us-east-1b',
    'East-#7':'us-east-1c',
    'East-#12':'us-east-1a',
    'West-#1':'us-west-2a',
    'West-#2':'us-west-2b',
    'West-#4':'us-west-2c',
    'West-#6':'us-west-1b',
    'West-#9':'us-west-1a'
             }
'''

'''
Abstract EC2 instances on-demand info from original file to a new file
'''
'''
with open(filename) as csvfile:
    reader=csv.DictReader(csvfile)
    newFilename=filename.split('.')[0]+"-new.csv"
    with open(newFilename,'w') as csvwritefile:
        writer=csv.DictWriter(csvwritefile,fieldnames=reader.fieldnames)    
        writer.writeheader()
        i=0
        for row in reader:
            usageType=row['UsageType'].split(':')[0]
            if(usageType=='SpotUsage' or usageType=='USW1-SpotUsage' or usageType=='USW2-SpotUsage' and row['UsageType'].split(':')[1]==row['ItemDescription'].split()[0]):           
            #if(row['AvailabilityZone']!=''):
                writer.writerow(row)
                i+=1
                print i
    csvwritefile.close()
csvfile.close()

print "done!"
'''

'''
Get Spot Instances from original file
'''

bill=[]
InstanceId={}
keyList=['StartTime','EndTime', 'Cost', 'NumOfInstances']
zones={}
instanceType={}
instanceDetail={}
instanceZone={}
with open(filename,'r') as csvfile:
    reader=csv.DictReader(csvfile)
    newFilename=filename.split('.')[0]+"-hourly.csv"
    i=0
    cost=0
    noOfInstance=0
    newRow={}
    for row in reader:
        try:
            usageType=row['UsageType'].split(':')[0]
            if(usageType=='SpotUsage' or usageType=='USW1-SpotUsage' or usageType=='USW2-SpotUsage' and row['UsageType'].split(':')[1]==row['ItemDescription'].split()[0]):
                instance=row['UsageType'].split(':')[1]
                InstanceId[row['ResourceId']]=1
                zone=row['ItemDescription'].split()
                if(usageType=='USW1-SpotUsage'):
                    zone=zone[6]+"-"+zone[12]
                else:
                    zone=zone[6]+"-"+zone[11]
                zone=zoneConvert[zone]
                zones[zone]=1
                startDate=datetime.datetime.strptime(row['UsageStartDate'],"%Y-%m-%d %H:%M:%S")
                endDate=datetime.datetime.strptime(row['UsageEndDate'],"%Y-%m-%d %H:%M:%S")
            
                if(row['ResourceId'] in list(instanceDetail.keys())):
                    instanceDetail[row['ResourceId']]['Detail'].append({'StartTime':startDate, 'EndTime':endDate, 'Cost':float(row['BlendedCost'])})
                    instanceDetail[row['ResourceId']]['TotalCost']+=float(row['BlendedCost'])
                else:
                    instanceDetail[row['ResourceId']]={'Detail':[],'TotalCost':0.0,'InstanceType':instance,'Zone':zone}
                    instanceDetail[row['ResourceId']]['Detail'].append({'StartTime':startDate, 'EndTime':endDate, 'Cost':float(row['BlendedCost'])})
                    instanceDetail[row['ResourceId']]['TotalCost']+=float(row['BlendedCost'])
            
                if(instance in list(instanceZone.keys())):
                    if(zone in list(instanceZone[instance].keys())):
                        if(row['UsageStartDate'] in list(instanceZone[instance][zone].keys())):
                            instanceZone[instance][zone][row['UsageStartDate']]['Count']+=1
                            if(float(row['BlendedCost']) != instanceZone[instance][zone][row['UsageStartDate']]['Cost'][0]):
                                instanceZone[instance][zone][row['UsageStartDate']]['Cost'].append(float(row['BlendedCost']))
                        else:
                            instanceZone[instance][zone][row['UsageStartDate']]={'Count':1,'Cost':[float(row['BlendedCost'])]}
                    else:
                        instanceZone[instance][zone]={row['UsageStartDate']:{'Count':1,'Cost':[float(row['BlendedCost'])]}}
                else:
                    instanceZone[instance]={zone:{row['UsageStartDate']:{'Count':1,'Cost':[float(row['BlendedCost'])]}}}
                    
                if(len(list(newRow.keys()))==0 or startDate!=newRow['StartTime']):
                    if(len(list(newRow.keys()))!=0):
                        newRow['Cost']=cost
                        newRow['NumOfInstances']=noOfInstance
                        for ins in instanceType:
                            if (ins in list(newRow.keys())):
                                newRow[ins+"_AVE"]=old_div(newRow[ins],newRow[ins+"_no"])
                        bill.append(newRow.copy())
                    cost=0
                    noOfInstance=0
                    newRow.clear()
                    for key in keyList:
                        newRow[key]=0
                    newRow['StartTime']=startDate
                    newRow['EndTime']=endDate
               
                noOfInstance+=float(row['UsageQuantity'])
                cost+=float(row['BlendedCost'])
                if(zone in list(newRow.keys())):
                    newRow[zone]+=1
                    newRow[zone+'_cost']+=float(row['BlendedCost'])
                else:
                    newRow[zone]=1
                    newRow[zone+'_cost']=float(row['BlendedCost'])
                if(instance in list(newRow.keys())):
                    newRow[instance]+=float(row['BlendedCost'])
                    newRow[instance+'_no']+=float(row['UsageQuantity'])
                else:
                    newRow[instance]=float(row['BlendedCost'])
                    newRow[instance+'_no']=float(row['UsageQuantity'])
                instanceType[instance]=1
                i+=1
                print("Row "+ str(i)+ " is complete!")
        except:
            print(row)
csvfile.close()
for key in list(zones.keys()):
    keyList.append(key)
    keyList.append(key+'_cost')
for key in list(instanceType.keys()):
    keyList.append(key)
    keyList.append(key+"_no")
    keyList.append(key+'_AVE')
with open(newFilename,'w') as csvwritefile:
    writer=csv.DictWriter(csvwritefile,fieldnames=keyList)
    writer.writeheader()
    for row in bill:
        writer.writerow(row)
csvwritefile.close()


'''
Processing data on-demand
'''

'''
billInfo=[]
keyList=['StartTime','EndTime', 'Cost', 'NumOfInstances']

def getRow(row):
    tmp=row.copy()
    return tmp

with open(filename,'r') as csvfile:
    reader=csv.DictReader(csvfile)
    i=0
    cost=0
    noOfInstance=0
    newRow={}
    for row in reader:
        instance=row['UsageType'].split(':')[1]
        startDate=datetime.datetime.strptime(row['UsageStartDate'],"%Y-%m-%d %H:%M:%S")
        endDate=datetime.datetime.strptime(row['UsageEndDate'],"%Y-%m-%d %H:%M:%S")
        
        if(len(newRow.keys())==0 or startDate!=newRow['StartTime']):
            if(len(newRow.keys())!=0):
                newRow['Cost']=cost
                newRow['NumOfInstances']=noOfInstance
                billInfo.append(getRow(newRow))
            cost=0
            noOfInstance=0
            for key in keyList:
                newRow[key]=0
            newRow['StartTime']=startDate
            newRow['EndTime']=endDate
            noOfInstance= float(row['UsageQuantity'])
            cost=float(row['BlendedCost'])
            newRow[row['AvailabilityZone']]+=1
        else:
            noOfInstance+=float(row['UsageQuantity'])
            cost+=float(row['BlendedCost'])
            newRow[row['AvailabilityZone']]+=1
csvfile.close()

outfile=filename.split('.')[0]+'-res.csv'
with open(outfile,'w') as csvfile:
    writer=csv.DictWriter(csvfile,fieldnames=keyList)
    writer.writeheader()
    for r in billInfo:
        writer.writerow(r)
csvfile.close()
'''

'''
This section of codes are used to compare the real charging market price with the price data in the database.
'''

import analysis_east
with open('detailedInstances.csv','w') as detailInstanceWriter:
    for k in list(instanceDetail.keys()):
        #sim=analysis.simulation(instanceDetail[k]['InstanceType'],instanceDetail[k]['Zone'])
        detailInstanceWriter.write(k+","+instanceDetail[k]['Zone']+","+instanceDetail[k]['InstanceType']+","+str(instanceDetail[k]['TotalCost'])+"\n")
        for dicts in instanceDetail[k]['Detail']:
            #price=sim.findPrice(dicts['StartTime'])
            detailInstanceWriter.write(",,,,"+dicts['StartTime'].strftime("%Y-%m-%dT%H:%M:%S.%f")+","+dicts['EndTime'].strftime("%Y-%m-%dT%H:%M:%S.%f")+","+str(dicts['Cost'])+"\n")
detailInstanceWriter.close()


'''
This section of codes is used to write detailed zone instance info
'''

with open('detailedInstanceZone.csv','w') as instanceZoneWriter:
    for i in list(instanceZone.keys()):
        for z in list(instanceZone[i].keys()):
            
            sim=analysis_east.simulation(i,z)
            for t in sorted(instanceZone[i][z].keys()):
                print(i+" "+z+" "+t)
                line=i+","+z+","+t+","+str(instanceZone[i][z][t]['Count'])+","
                for p in instanceZone[i][z][t]['Cost']:
                    line+=str(p)+","
                price=sim.findPrice(datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S"))
                st=sim.priceStatistic(datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S"), 3600)
                instanceZoneWriter.write(line+","+str(price)+","+str(st[0])+","+str(st[1])+","+str(st[2])+","+str(st[3])+"\n")
instanceZoneWriter.close()


print("All done!\n")

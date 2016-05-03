'''
Created on Sep 5, 2015

@author: tlisowski
'''
from lxml import html
import requests
import os
import csv
import json
from threading import Thread, Lock
from datetime import datetime, timedelta
import socket
from ipwhois import IPWhois 
import urllib3.contrib.pyopenssl
import time
class WebContentCrawler(object):
    '''
    Web Crawler for web page content analysis system
    '''
    
    '''
    Constructor 
    @param webPageListPath: path to .csv file having Alexa 1M web pages
    '''
    def __init__(self, webPageListPath,):
        '''
        Constructor
        '''
        self.webpageListPath=webPageListPath;
        #Max threads that can be active at one time
        self.threadMax=175;
        #number of active threads
        self.activeThreads=0;
        #number of completed threads
        self.completedThreads=0;
        #mutex for synchronization
        self.mutex=Lock();
        #mutex to examine latencies
        self.webContentLatencyMutex=Lock();
        self.ipWhoIsLatencyMutex=Lock();
        self.ipWhoIsLatencyFile=open('ipWhoIsLatency.csv','a');
        self.webContentLatencyFile=open('webLatency.csv','a');
        
        #total pages to be fetched
        self.totalPages=0;
        #fix for SSL issues with python library
        urllib3.contrib.pyopenssl.inject_into_urllib3();
        return;
    
    
    def __del__(self):
        self.ipWhoIsLatencyFile.close();
        self.webContentLatencyFile.close();
        
        
    '''
    getIPandWhoIsData maps domain tot IP and gets whois data for the IP address
    @param url: Domain to map to IP and get whoisdata for
    
    @return: dictonary containing domain as key and whois info as value
    '''
    def getIPandWhoIsData(self,url):
        try:
            ip=socket.gethostbyname(url);
            obj=IPWhois(ip);
            timeBefore=time.time();
            whoIsDict=obj.lookup();
            timeAfter=time.time();
            latency=timeAfter-timeBefore;
            self.ipWhoIsLatencyMutex.acquire();
            self.ipWhoIsLatencyFile.write(url+','+str(latency)+'\n');
            self.ipWhoIsLatencyMutex.release();
            whoIsDict['resolved_IP']=ip;
            return {url : whoIsDict};
        except Exception:
            return dict();
    
    '''
    storeIP handles taking accumulated IPwhois data and store it as json files
    @param ipDict: dictionary of domains and whois data
    @param timePath: path to store json files 
    '''
    def storeIP(self,ipDict,timePath):
        if not os.path.exists(timePath):
            os.makedirs(timePath);
        for key in ipDict:
            try:
                #print timePath+key;
                f= open(timePath+key+'.json','a');
                json.dump(ipDict[key],f);
                f.close();
            except Exception:
                os.remove(timePath+key+'.json');
        return;
           
    '''
    fetchDomTree gets webpage for given url
    
    @param url: url to fetch page 
    
    @return: dictionary containing web page content as DOM tree
    '''
    def fetchDomTree(self,url):
        try:
            completeUrl='http://'+url;
            timeBefore=time.time();
            page= requests.get(completeUrl,stream=True,timeout=3);
            timeAfter=time.time();
            latency=timeAfter-timeBefore;
            tree= html.fromstring(page.content);
            self.webContentLatencyMutex.acquire();
            self.webContentLatencyFile.write(url+','+str(latency)+'\n');
            self.webContentLatencyMutex.release();
        except Exception:
            try:
                completeUrl='https://'+url;
                timeBefore=time.time();
                page= requests.get(completeUrl,stream=True,timeout=3,verify=False);
                timeAfter=time.time();
                latency=timeAfter-timeBefore;
                tree= html.fromstring(page.content);
                self.webContentLatencyMutex.acquire();
                self.webContentLatencyFile.write(url+','+str(latency)+'\n');
                self.webContentLatencyMutex.release();
            except Exception:
                return dict();
        
        return {url : tree}
    
    '''
    fetchAndUpdateDict fetches data for a domain and updates the accumulation dictionaries
    @param url: domain(url) to fetch data for 
    @param urlTreeDict: dictionary contaning accumulated url and web content data
    @param ipdict: dictionary containing whois data for resolved IPs  
    '''
    def fetchAndUpdateDict(self,url,urlTreeDict,ipdict):
        tempDict= self.fetchDomTree(url);
        tempIPDict=self.getIPandWhoIsData(url);
        self.mutex.acquire();
        urlTreeDict.update(tempDict);
        ipdict.update(tempIPDict);
        #print "in fetch Update Dict"
        #print urlTreeDict
        self.completedThreads=self.completedThreads+1;
        self.activeThreads=self.activeThreads-1;
        self.mutex.release();
        return;
    
    '''
    storeTree takes in domain and web content dictionary and stores it in a .html files
    @param urlDomTreeDictionary: dictionary containing web content data
    @param timePath: directory to store content
    '''
    def storeTree(self,urlDomTreeDictionary,timePath):
        #add in iterator for list
        if not os.path.exists(timePath):
            os.makedirs(timePath);
        for key in urlDomTreeDictionary:
            try:
                f= open(timePath+key+'.html','a');
                f.write(html.tostring(urlDomTreeDictionary[key]));
                f.close();
            except Exception:
                os.remove(timePath+key+'.html');
        return;
    
    '''
    loadTreeFromMem loads a stored webpage as a DOM tree
    @param path: file to load webpage from
    
    @return: DOM tree of stored web page
    '''
    def loadTreeFromMem(self,path):
        f= open(path,'r');
        tree=html.fromstring(f.read());
        f.close();
        return tree;
    
    '''
    loadIpDataFromMem loads whois IP data from a stored .json file
    @param path: file to load whois data from
    
    @return: dictionary containing ipwhois data
    '''
    def loadIpDataFromMem(self,path):
        f=open(path,'r');
        ipDict=json.load(f);
        f.close();
        return ipDict;
    
    '''
    fetchAndStoreTopPages fetches range of pages from the Alexa Top 1M and stores them in directory based on time fetched
    @param startPage: page rank to start fetch from
    @param numPages: number of pages to fetch
    @param time: time of fetch
    '''
    def fetchAndStoreTopPages(self,startPage,numPages,time):
        self.totalPages=numPages;
        storeCheckPoint=0;
        storeInteval=self.threadMax;
        timeString=str(time.year)+'_'+str(time.month)+'_'+str(time.day)+'_'+str(time.hour)+'/';
        f= open(self.webpageListPath,'r');
        csvReader=csv.reader(f,delimiter=',');
        tempNumPages= numPages;
        urlTreeDict={};
        iPDict={};
        newCheck=storeCheckPoint*storeInteval+storeInteval;
        checkPoint= min(newCheck,numPages);
        startPage=startPage-1;
        #get to starting page in csv file
        while startPage>0:
            next(csvReader);
            startPage-=1;
        
        #start fetching data
        while True:
            self.mutex.acquire();
            #if active thread limit not reached, spawn another fetching thread
            if self.activeThreads<self.threadMax and self.completedThreads+self.activeThreads < self.totalPages:
                row=next(csvReader);
                t= Thread(target=self.fetchAndUpdateDict, args=(row[1],urlTreeDict,iPDict));
                #run in background
                t.daemon=True;
                t.start();
                self.activeThreads=self.activeThreads+1;
            #if at storing checkpoint, store the data
            if self.completedThreads>=checkPoint:
                self.storeTree(urlTreeDict, 'web/'+timeString);
                urlTreeDict.clear();
                self.storeIP(iPDict, 'ip/'+timeString);
                iPDict.clear();
                storeCheckPoint=storeCheckPoint+1;
                newCheck=storeCheckPoint*storeInteval+storeInteval;
                checkPoint= min(newCheck,numPages);
            #if all pages fetched, break main while loop
            if self.completedThreads==self.totalPages:
                break;
            self.mutex.release();
        self.mutex.release();
        #reset class variables for next call
        self.completedThreads=0;
        self.activeThreads=0;
        f.close();
        return;

    '''
    getPagesInTime returns historic page content and whois data for the resolved ip
    @param url: domain(url) to fetch content for
    @param startDate: begininning date to get data from. In form [year,month,day,hour]
    @param differenceFormat: amount of time to go back from start date to get historic fetch from start date
    in form [weeks,days,hours] back
    
    @return: dictionary containing whois data and page content for selected domain
    '''
    def getPagesInTime(self,url,startDate,differenceFormat):
        #Difference format is [weeks,days,hours];
        #Start date is [year, month, day, hour]
        for i in differenceFormat:
            if not isinstance(i,int):
                print 'ERROR: ALL VALUES NEED TO BE INTS';
                return list();
        dateDiff=timedelta(hours=differenceFormat[2],days=differenceFormat[1],weeks=differenceFormat[0]);
        startDateString=str(startDate[0])+'_'+str(startDate[1])+'_'+str(startDate[2])+'_'+str(startDate[3]);
        endDate=datetime(startDate[0],startDate[1],startDate[2],startDate[3])-dateDiff;
        endDateString=str(endDate.year)+'_'+str(endDate.month)+'_'+str(endDate.day)+'_'+str(endDate.hour);
        if not (os.path.exists('web/') and os.path.exists('ip/')):
            print 'Directory doesnt exist'
            return list();
        dirList=sorted(os.listdir('web/'),reverse=True);
        if len(dirList)<2:
            #not enough for difference
            return list();
        actualStartTime='';
        actualEndTime='';
        #look for closest fetch date to start and end time
        for i in range(0,len(dirList)):
            if actualStartTime=='':
                if startDateString >= dirList[i]:
                    actualStartTime=dirList[i];
                    #to ensure end date gets next one
                    continue;
            if actualEndTime=='':
                if endDateString>= dirList[i]:
                    actualEndTime=dirList[i];
                    continue;
            if actualStartTime!='' and actualEndTime!='':
                break;
        #handle corner case if times too far in past
        if actualStartTime=='' or actualEndTime=='':
            if actualStartTime=='' or actualStartTime==dirList[-1]:
                #set both start time will always get set first
                actualStartTime=dirList[-2];
                actualEndTime=dirList[-1];
            else:
                #know endTime is only thing that has not been set
                actualEndTime=dirList[-1];
                
        startPage=self.loadTreeFromMem('web/'+actualStartTime+'/'+url+'.html');
        startIpData=self.loadIpDataFromMem('ip/'+actualStartTime+'/'+url+'.json');
        endPage=self.loadTreeFromMem('web/'+actualEndTime+'/'+url+'.html');
        endIpData=self.loadIpDataFromMem('ip/'+actualEndTime+'/'+url+'.json');
        returnDict=dict();
        returnDict['start']=[actualStartTime,startPage,startIpData];
        returnDict['past']=[actualEndTime,endPage,endIpData];
        return returnDict; 
        
        

    
    
    def processPage(self,url):
        return;
    
    
            
            
            
            
            
            
            
            
            
            
            
            
        
        
    
        
        
        
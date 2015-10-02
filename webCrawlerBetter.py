'''
Created on Sep 5, 2015

@author: tlisowski
'''
from lxml import html
import requests
import os
import csv
from threading import Thread, Lock
from datetime import datetime

class WebContentCrawler(object):
    '''
    Web Crawler for web page content analysis system
    '''
    

    def __init__(self, webPageListPath,):
        '''
        Constructor
        '''
        self.webpageListPath=webPageListPath;
        self.threadMax=100;
        self.activeThreads=0;
        self.completedThreads=0;
        self.mutex=Lock();
        self.totalPages=0;
        return;
    
    def fetchDomTree(self,url):
        try:
            completeUrl='http://'+url;
            page= requests.get(completeUrl,stream=True);
            tree= html.fromstring(page.content);
        except Exception:
            try:
                completeUrl='https://'+url;
                page= requests.get(completeUrl,stream=True);
                tree= html.fromstring(page.content);
            except Exception:
                return dict();
        
        return {url : tree}
    
    def fetchAndUpdateDict(self,url,urlTreeDict):
        tempDict= self.fetchDomTree(url);
        self.mutex.acquire();
        urlTreeDict.update(tempDict);
        #print "in fetch Update Dict"
        #print urlTreeDict
        self.completedThreads=self.completedThreads+1;
        self.activeThreads=self.activeThreads-1;
        self.mutex.release();
        return;
    
    def storeTree(self,urlDomTreeDictionary,timePath):
        #add in iterator for list
        if not os.path.exists(timePath):
            os.makedirs(timePath);
        for key in urlDomTreeDictionary:
            f= open(timePath+key+'.html','a');
            f.write(html.tostring(urlDomTreeDictionary[key]));
            f.close();
        return;
    
    def loadTreeFromMem(self,path):
        f= open(path,'r');
        tree=html.fromstring(f.read());
        f.close();
        return tree;
    
    def fetchAndStoreTopPages(self,numPages):
        self.totalPages=numPages;
        storeCheckPoint=0;
        storeInteval=100;
        time=datetime.now()
        timeString=str(time.year)+'_'+str(time.month)+'_'+str(time.day)+'_'+str(time.hour)+'/';
        f= open(self.webpageListPath,'r');
        csvReader=csv.reader(f,delimiter=',');
        tempNumPages= numPages;
        urlTreeDict={};
        newCheck=storeCheckPoint*storeInteval+storeInteval;
        checkPoint= min(newCheck,numPages);
        while True:
            self.mutex.acquire();
            if self.activeThreads<self.threadMax and self.completedThreads+self.activeThreads < self.totalPages:
                row=next(csvReader);
                print row;
                t= Thread(target=self.fetchAndUpdateDict, args=(row[1],urlTreeDict));
                t.daemon=True;
                t.start();
                self.activeThreads=self.activeThreads+1;
            if self.completedThreads>=checkPoint:
                self.storeTree(urlTreeDict, 'web/'+timeString);
                urlTreeDict.clear();
                storeCheckPoint=storeCheckPoint+1;
                newCheck=storeCheckPoint*storeInteval+storeInteval;
                checkPoint= min(newCheck,numPages);
            if self.completedThreads==self.totalPages:
                break;
            self.mutex.release();
        self.mutex.release();
        return;




    
    
    def processPage(self,url):
        return;
    
    
            
            
            
            
            
            
            
            
            
            
            
            
        
        
    
        
        
        
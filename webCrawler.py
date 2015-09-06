'''
Created on Sep 5, 2015

@author: tlisowski
'''
from lxml import html
import requests
import os
import csv
import threading
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
        self.threadMax=10;
        return;
    
    def fetchDomTree(self,url):
        completeUrl='http://'+url;
        page= requests.get(completeUrl,stream=True);
        tree= html.fromstring(page.content);
        return {url : tree}
    
    def fetchAndUpdateDict(self,url,urlTreeDict):
        tempDict= self.fetchDomTree(url);
        urlTreeDict.update(tempDict);
        return;
    
    def storeTree(self,urlDomTreeDictionary,timePath):
        #add in iterator for list
        if not os.path.exists(timePath):
            os.makedirs(timePath)
        for key in urlDomTreeDictionary:
            f= open(timePath+key+'.html','a');
            f.write(html.tostring(urlDomTreeDictionary[key]));
            f.close();
        return;
    
    def loadTreeFromMem(self,path):
        f= open(path,'r');
        tree=html.fromstring(f.read());
        return tree;
    
    def fetchAndStoreTopPages(self,numPages):
        time=datetime.now()
        timeString=str(time.year)+'_'+str(time.month)+'_'+str(time.day)+'_'+str(time.hour)+'/';
        f= open(self.webpageListPath,'r');
        csvReader=csv.reader(f,delimiter=',');
        tempNumPages= numPages;
        urlTreeDict={};
        threadList=[];
        for row in csvReader:
            if tempNumPages <= 0:
                break;
            tempNumPages-=1;
            t= threading.Thread(target=self.fetchAndUpdateDict, args=(row[1],urlTreeDict));
            t.daemon=False;
            t.start();
            threadList.append(t);
            if len(threadList)>=self.threadMax:
                for i in threadList:
                    i.join();
                del threadList[:];
            self.storeTree(urlTreeDict, 'web/'+timeString);
            urlTreeDict.clear();
            
        for i in threadList:
            i.join();
        self.storeTree(urlTreeDict, 'web/'+timeString);
        return;
    

    
    
    def processPage(self,url):
        return;
    
    
            
            
            
            
            
            
            
            
            
            
            
            
        
        
    
        
        
        
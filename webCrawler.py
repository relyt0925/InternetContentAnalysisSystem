'''
Created on Sep 5, 2015

@author: tlisowski
'''
from lxml import html
import requests
import sys
import os
import csv
import codecs

class WebContentCrawler(object):
    '''
    Web Crawler for web page content analysis system
    '''


    def __init__(self, webPageListPath,):
        '''
        Constructor
        '''
        self.webpageListPath=webPageListPath;
        return;
    
    def fetchDomTree(self,url):
        completeUrl='http://'+url;
        page= requests.get(completeUrl,stream=True);
        tree= html.fromstring(page.content);
        return {url : tree}
    
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
    
    def fetchTopPages(self,numPages):
        f= open(self.webpageListPath,'r');
        csvReader=csv.reader(f,delimiter=',');
        tempNumPages= numPages;
        urlTreeDict={};
        for row in csvReader:
            tempDict= self.fetchDomTree(row[1]);
            urlTreeDict.update(tempDict);
            tempNumPages-=1;
            if tempNumPages <= 0:
                break;
        return urlTreeDict;

    
    
    def processPage(self,url):
        return;
    
    
            
            
            
            
            
            
            
            
            
            
            
            
        
        
    
        
        
        
'''
Created on Sep 6, 2015

@author: tlisowsk
'''
from webCrawlerBetter import WebContentCrawler
from datetime import datetime
from lxml import html

def webCrawlerDriver():
    webCrawler=WebContentCrawler('top-1m.csv');
    time=datetime.now();
    webCrawler.fetchAndStoreTopPages(1,5000,time);
    webCrawler.fetchAndStoreTopPages(150000,5000,time);
    #time=datetime.now()
    #timeString=str(time.year)+'_'+str(time.month)+'_'+str(time.day)+'_'+str(time.hour)+'/';
    #webCrawler.storeTree(pages, 'web/'+timeString);
    #cmpTree=webCrawler.loadTreeFromMem('web/'+timeString+'google.com.html');
    #print html.tostring(cmpTree);
    return;
            
        

def testPageFetcher():
    webCrawler=WebContentCrawler('top-1m.csv');
    time=datetime.now();
    #returnDict=webCrawler.getPagesInTime('google.com',[time.year,time.month,time.day,time.hour],[0,0,0]);
    returnDict=webCrawler.getPagesInTime('google.com',[time.year,time.month,time.day,time.hour],[3,0,0]);
    for key in returnDict:
        print returnDict[key][0];
    return;
    
    

if __name__ == '__main__':
    #testPageFetcher();
    webCrawlerDriver();
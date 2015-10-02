'''
Created on Sep 6, 2015

@author: tlisowsk
'''
from webCrawlerBetter import WebContentCrawler
from datetime import datetime
from lxml import html

def webCrawlerDriver():
    webCrawler=WebContentCrawler('top-1m.csv');
    webCrawler.fetchAndStoreTopPages(100);
    time=datetime.now()
    timeString=str(time.year)+'_'+str(time.month)+'_'+str(time.day)+'_'+str(time.hour)+'/';
    #webCrawler.storeTree(pages, 'web/'+timeString);
    cmpTree=webCrawler.loadTreeFromMem('web/'+timeString+'google.com.html');
    #print html.tostring(cmpTree);
    return;
            
        



if __name__ == '__main__':
    webCrawlerDriver();
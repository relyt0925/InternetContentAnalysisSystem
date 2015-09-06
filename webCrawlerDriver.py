'''
Created on Sep 6, 2015

@author: tlisowsk
'''
from webCrawler import WebContentCrawler
import os
from datetime import datetime
from lxml import html

def webCrawlerDriver():
    webCrawler=WebContentCrawler('top-1m.csv');
    pages=webCrawler.fetchTopPages(3);
    time=datetime.now()
    timeString=str(time.year)+'_'+str(time.month)+'_'+str(time.day)+'_'+str(time.hour)+'/';
    webCrawler.storeTree(pages, 'web/'+timeString);
    cmpTree=webCrawler.loadTreeFromMem('web/'+timeString+'google.com.html');
    if html.tostring(cmpTree) == html.tostring(pages['google.com']):
        print str(True);
    for key in pages:
        print key;
        #print pages[key];
    return;
            
        



if __name__ == '__main__':
    webCrawlerDriver();
'''
Created on Sep 6, 2015

@author: tlisowsk
'''
import os
import json
import sys
import htmlDiff
import jsonpickle

'''Gets differences between all webpages fetched between two time periods and stores them in files
@param startPath:Path to original web pages to do comparison based on (typically earlier in time)
@param endPath: Path to webPages to look at changes from the original web pages (typically later in time) 
@return stores in files under directory <startDate>_<endDate>/<domainFetched>.html.
Format is a json string that needs to be decoded with jsonpickle in order to get proper results.
'''
def diffDriver(startPath,endPath): 
    #Make sure paths exist or else exit  
    if not os.path.exists(startPath):
        print "Start Path Does Not Exist"
        return;
    if not os.path.exists(endPath):
        print "End Path Does Not Exist";
        return;
    startPathFileList=os.listdir(startPath);
    endPathFileList=os.listdir(endPath);
    #Simple check to see if path contains html content, NOTE: CAN STILL FAIL
    #Only checks first in list
    if not startPathFileList[0].endswith('.html'):
        print "Need directory of all historical html files for start date";
        return;
    if not endPathFileList[0].endswith('.html'):
        print "Need directory of all historical html files for end date";
        return;
    #extract date
    startDate='';
    endDate='';
    startDate=startPath[startPath.find('2015'):len(startPath)-1];
    endDate=endPath[endPath.find('2015'):len(endPath)-1];
    #create directory based on the compared dates
    diffOutputDirectory=startDate+'_'+endDate+'/';
    if not os.path.exists(diffOutputDirectory):
        os.makedirs(diffOutputDirectory);
    
    #iterate through all files and do diff
    #ONLY does diff if webpage is fetched in both time periods
    for file in startPathFileList:
        try:
            startFile= startPath+file;
            endFile= endPath+file;
            #print startFile;
            #print endFile;
            if not file.endswith('.html'):
                continue;
            #Run files through HTML differ
            diffOutput=htmlDiff.htmldiff(startFile,endFile);
            #Serialize to file
            diffOutputEncoded=jsonpickle.encode(diffOutput);
            outfile=open(diffOutputDirectory+file, 'w');
            json.dump(diffOutputEncoded, outfile);
            outfile.close();
            #NOTE: HERE IS HOW TO READ FROM THE SERIALIZED FILE BACK TO PYTHON OBJECT
            #f=open(diffOutputDirectory+file,'r');
            #newDiffOutput=jsonpickle.decode(json.load(f));
            #f.close();
        except Exception as e:
            #most likely due to webpage not fetched in time, or beautiful soup erroring because 
            #the webpage is not properly formatted
            #outfile.close();
            print e;
            continue;
    return;           
    
    

if __name__ == '__main__':
    if len(sys.argv) == 3:
        f1 = sys.argv[1];
        f2 = sys.argv[2];
        diffDriver(f1,f2);
    else:
        print "arg1: startDatePath";
        print "arg2: endDatePath";
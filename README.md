# webAnalysisSystem
ECE 8813 Content Analysis System

Best practice is to run all commands in the main directory where the git repo is created.

*Note: will create historical content directories in directory wherever crawler is ran*

To run web crawler:

python webCrawlerDriver.py

All our historical data is under /nethome/tlisowski3/gatechContentAnalysis/web & /nethome/tlisowski3/gatechContentAnalysis/ip/
Results in directories formatted as "year_month_day_hour" that the fetching started. 
Under each directory are all the historical results for that fetch. 
ip contains the IP whois data and web contains the web content for the domain names.

htmlDifferDriver automates and serializing the diffing results for all the web pages fetched in two historical time periods.

To run htmlDifferDriver:

python htmlDiffDriver.py path/to/earlierDateContent path/to/laterDateContent

Ex) python htmlDiffDriver.py web/2015_10_30_4/ web/2015_11_9_22/
    -the two directories above lead to historical web content that wants to be compared

htmlDiff is the diffing engine. It outputs the differences between two web pages.

To run htmlDiff:

python htmlDiff.py /path/to/earlierWebPage /path/to/laterWebPage

Ex) python htmlDiff.py web/2015_10_30_4/google.com.html web/2015_11_9_22/google.com.html 

Features can be calculated using the methods in features.py. A script is used
to generate the training vectors for the classifier. The training vectors can be
recalculated using:

python makeTrainingSet.py

The output csv, training_vectors.csv can be opened in Weka, and a classifier can
be trained and evaluated using 10-fold cross validation using the output feature
vectors.

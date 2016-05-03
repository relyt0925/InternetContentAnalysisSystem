All you need to do to lookup a domain on Googles Safe Browsing List(GSBL) is as follows:

1. Wherever you're writing your code just add the lines

from gsb import getDomainStatus 
url='www.avtobanka.ru' #example domain,can be anything
response=getDomainStatus(url)


2.Things to NOTE:

-GSBL categorizes malicious domains into unwanted,malware or phishing.
-So the 'response' variable above can hold safe(i.e no match on GSBL), unwanted(match on GSBL),phishing(match on GSBL)or malware(match on GSBL)
-In gsb.py I have provided my own google key so you dont need to get one(don't make it public or something). It is limited to 10,000 lookups  per day.
-Also, I have made several changes to the safebrowsinglookup.py by Julien Sobrier so that it matches our needs.

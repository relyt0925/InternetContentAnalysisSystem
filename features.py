from __future__ import division
import htmlDiff
import sys
import string
import pdb
from GSB.gsb import getDomainStatus
from pprint import *

def getCSVHeaders():
    headers = []
    headers.append('elementType')
    headers.append('editType')
    headers.append('scriptLength')
    headers.append('specialCharRatio')
    headers.append('GSB')
    headers.append('jsEval')
    return headers

elementTypesList = ['a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio', 'b', 'base', 'basefont', 'bdi', 'bdo', 'bgsound', 'big', 'blink', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'command', 'content', 'data', 'datalist', 'dd', 'del', 'details', 'dfn', 'dialog', 'dir', 'div', 'dl', 'dt', 'element', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset', 'head', 'header', 'hgroup', 'hr', 'html', 'i', 'iframe', 'image', 'img', 'input', 'ins', 'isindex', 'kbd', 'keygen', 'label', 'legend', 'li', 'link', 'listing', 'main', 'map', 'mark', 'marquee', 'menu', 'menuitem', 'meta', 'meter', 'multicol', 'nav', 'nobr', 'noembed', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'picture', 'plaintext', 'pre', 'progress', 'q', 'rp', 'rt', 'rtc', 'ruby', 's', 'samp', 'script', 'section', 'select', 'shadow', 'small', 'source', 'spacer', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr', 'xmp']
elementTypes = {}

def createElementTypesDict():
    global elementTypes
    for i, elementType in enumerate(elementTypesList):
        elementTypes[elementType] = i

# Map each element type to a numerical value for the feature vector.
def getElementID(diff):
    global elementTypes
    elementType = diff['elementType']
    # Remove _1 from script_1 and stuff into the script bucket
    try:
        return elementTypes[elementType.split('_')[0]]
    except KeyError:
        elementTypesList.append(elementType.split('_')[0])
        elementTypes[elementType.split('_')[0]] = len(elementTypesList)
        return elementTypes[elementType.split('_')[0]]
    except:
        diff['elementType'] = 'builtin_function_or_method'
        return -1

def printElementTypes():
    pprint(sorted(elementTypes.keys()))

changeTypes = {}
# Map each change types to a numerical value for the feature vector.
def getChangeID(otherInfo):
    try:
        return changeTypes[otherInfo]
    except:
        changeTypes[otherInfo] = len(changeTypes.keys())
        return changeTypes[otherInfo]

# Calculate the length of the script that is to be run.
def scriptLen(change):
    try:
        if 'script' in change['elementType']:
            try:
                return len(change['afterText'])
            except:
                return 0
        else:
            return -1
    except:
        return -1

# Calculate the number of special characters the change has.
def specialCharRatio(change):
    specialCount = 0
    normalCount = 0
    try:
        for char in string.punctuation:
            specialCount += change['afterText'].count(char)
        normalCount = len(change['afterText']) - specialCount
        return specialCount / normalCount
    except ZeroDivisionError:
        return -1
    except AttributeError:
        return -1

def getGSB(change):
    try:
        url = change['afterAttribute']['src']
        response=getDomainStatus(url)
        if response == 'malware':
            return 1
        elif response == 'phishing':
            return 2
        elif response == 'unwanted':
            return 3
        else:
            return 0
    except KeyError:
        return -1
    except TypeError:
        return -1

def jsEval(change):
    try:
        if change['elementType'] == 'script':
            counts = change['afterText'].count('eval')
            counts += change['afterText'].count('document.write')
            counts += change['afterText'].count('document.createElement')
            #print 'eval counts {}'.format(counts)
            return counts
        return -1
    except AttributeError:
        return -1

# Return a list of feature vectors for the files.
def getFeatures(diff):
    # Calculate all of the changes in a page.
    createElementTypesDict()
    features = []

    # Open a CSV file and write each set of calculated features to a line.
    for key in sorted(diff.keys()):
        change = diff[key]
        f1 = getElementID(change)
        f2 = getChangeID(change['otherInfo'])
        f3 = scriptLen(change)
        f4 = specialCharRatio(change)
        f5 = getGSB(change)
        f6 = jsEval(change)
        featureRow = []
        featureRow.append(f1)
        featureRow.append(f2)
        featureRow.append(f3)
        featureRow.append(f4)
        featureRow.append(f5)
        featureRow.append(f6)
        features.append(featureRow)

    return features

if __name__ == "__main__":
    #file1 = sys.argv[1]
    #file2 = sys.argv[2]
    file1 = 'ground_truth/malware_traffic_analysis/2015_10_20_before'
    file2 = 'ground_truth/malware_traffic_analysis/2015_10_20_after'
    diff = htmlDiff.htmldiff(file1, file2)
    try: 
        outputDict['afterText'].rstrip()
    except:
        pass
    try: 
        outputDict['rawChange'].rstrip()
    except:
        pass
    features = getFeatures(diff)


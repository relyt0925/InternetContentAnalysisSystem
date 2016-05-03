# DIFF v1.5
from lxml import etree
from lxml.html.soupparser import parse, fromstring
import xml.etree.ElementTree as ET
import difflib
from BeautifulSoup import BeautifulSoup
import os
from difflib import SequenceMatcher

"""In order for our algorithm to work, we must make the elment names unique
   lxml names every child according to its type image, script, body, etc
   We have a uniques path to get to nodes in the tree """

def makeChildNamesUnique(node, key, isChangeTree, originalFileHash):
    children    = node.getchildren()
    uniqueSet   = {}
    checkedKeys = [] #Used for performance optimazation

    if isChangeTree:    #Check to see if this is the original or modified
        if "/!!/" in key:
            finish = key.rfind("/!/")
            path = key[:finish] + '/!!/' + key[finish + 3:] + '/!/'
        else:
            path = key

        matchingSubset = slicedict(originalFileHash, path) #Find possible matches in other tree
    #Go through each child node and rename it based on
    #1. If this is the orginal tree? or
    #2. Have we seen this name before
    for child in children:
        if isChangeTree:
            maxTag = None
            maxScore = 0
            didFindSimilarMatch = False

            elementString1 = removeExtraChars(
                etree.tostring(child))

            for originalFileKey in matchingSubset:  # Cycle through all new keys
                if originalFileKey in checkedKeys:
                    continue

                elementString2 = removeExtraChars(
                    etree.tostring(originalFileHash[originalFileKey]))

                temp = similar(elementString1, elementString2)
                try:
                    if temp > maxScore and child.tag in originalFileKey:
                        maxScore = temp
                        finish = originalFileKey.rfind("/!/")
                        maxTag = originalFileKey[finish + 3:]
                        didFindSimilarMatch = True
                        if maxScore == 1:  #Perfect match
                            checkedKeys.append(originalFileKey)
                            break
                except TypeError:  #Escape Comments
                    continue
            #Do the actual renaming based on the match above
            try:
                if didFindSimilarMatch and child.tag in maxTag:
                    if maxTag in uniqueSet:
                        if maxScore > uniqueSet[maxTag]:
                            for tempChild in children:
                                if tempChild.tag == maxTag:
                                    tempTag = generateTag(
                                        tempChild, child.tag, uniqueSet, False)
                                    tempChild.tag = tempTag
                                    uniqueSet[tempTag] = 0
                                    break

                            child.tag = maxTag
                            uniqueSet[maxTag] = maxScore
                        else:
                            tempTag = generateTag(
                                child, child.tag, uniqueSet, True)
                            continue
                    else:
                        child.tag = maxTag
                        uniqueSet[maxTag] = maxScore
                else:
                    tempTag = generateTag(child, child.tag, uniqueSet, True)
            except TypeError:
                pass
        else: #We are utilizing the original file, just generate new Tag
            generateTag(child, child.tag, uniqueSet, True)
    return node

""" Generates new tags """

def generateTag(child, tag, mySet, doRename):
    if tag in mySet:  # Make every child tag unique
        i = 1
        while True:
            tempkey = '%s_%d' % (tag, i)
            if tempkey in mySet:  # Have we seen this tag already
                i = i + 1
                continue
            else:  # No,so add it to the set
                if doRename:
                    try:
                        child.tag = tempkey
                        mySet[tempkey] = 0
                        break
                    except AttributeError:  # Catches immutable nodes
                        return tag
                else:
                    return tempkey

    else:  # Its not in the set so add it
        if doRename:
            mySet[tag] = 0
        return tag

""" Recursive function used to create a hash map of all the leaf
    nodes in an html file"""


def hashNodes(tree, data, isleaf, isChangeTree, originalFileHash):
    for node in tree:
        if node.getchildren():  # if true, not a leaf
            key = hashSingleNode(node, data, isleaf, 0)
            node = makeChildNamesUnique(
                node, key, isChangeTree, originalFileHash)

            # Recursive call to go deeper into the tree
            hashNodes(node, data, isleaf, isChangeTree, originalFileHash)
        else:  # This node must be a leaf node
            hashSingleNode(node, data, isleaf, 1)

def hashSingleNode(node, data, isleaf, mark):
    key = node.tag
    if node.getparent():
        parent_node = node.getparent()
        tempKey = parent_node.tag
        while parent_node.getparent():
            parent_node = parent_node.getparent()
            tempKey = parent_node.tag + '/!!/' + tempKey
        key = '%s/!/%s' % (tempKey, key)
    if key in data:  # Handles duplicate paths like 2 scripts inside a body tag, (Shouldnt be called!)
        i = 1
        while True:
            tempkey = '%s_%d' % (key, i)
            if tempkey in data:
                i = i + 1
                continue
            else:
                key = tempkey
                data[key] = node  # Put element in hashmap
                if mark == 1:
                    isleaf[key] = True  # This tag belongs to a leaf node
                else:
                    isleaf[key] = False  # This tag belongs to a parent node
                break
    else:
        data[key] = node
        if mark == 1:
            isleaf[key] = True
        else:
            isleaf[key] = False
    return key

""" Function used to store any changes inside a dictionary"""


def reportChange(
        outputDict,
        afterText,
        rawChange,
        elementType,
        listOfStringOperations,
        fullText,
        otherInfo=""):
    output = {}
    for op in listOfStringOperations:
        output['afterText'] = afterText
        output['rawChange'] = rawChange
        output['elementType'] = elementType
        output['op'] = op
        output['fullText'] = fullText
        output['otherInfo'] = otherInfo
        outputDict[getDiffOutputNumber(outputDict)] = output


""" Online Function I found to find changes between two strings and output it with tags"""


def show_diff(seqm):
    """Unify operations between two compared strings
       seqm is a difflib.SequenceMatcher instance whose a & b are strings"""
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<ins>" + seqm.b[b0:b1] + "</ins>")
        elif opcode == 'delete':
            output.append("<del>" + seqm.a[a0:a1] + "</del>")
        elif opcode == 'replace':
            output.append("<replace>" + seqm.a[a0:a1] + "</replace>")
            #raise NotImplementedError, "what to do with 'replace' opcode?"
        else:
            raise RuntimeError("unexpected opcode")
    return ''.join(output)


""" Function to elegantly report any text mismatches"""


def reportStringChange(outputDict, stringA, stringB, tag, otherInfo=""):
    if stringA is None:
        stringA = ""

    if stringB is None:
        stringB = ""

    textChange = show_diff(difflib.SequenceMatcher(None, stringA, stringB))
    soup = BeautifulSoup(textChange)
    insertTags = soup.findAll('ins')
    deleteTags = soup.findAll('del')
    replaceTags = soup.findAll('replace')
    for i in insertTags:
        reportChange(
            outputDict,
            stringB,
            i.text,
            tag,
            ['ins'],
            textChange,
            otherInfo)
    for d in deleteTags:
        reportChange(
            outputDict,
            stringB,
            d.text,
            tag,
            ['del'],
            textChange,
            otherInfo)
    for r in replaceTags:
        reportChange(
            outputDict,
            stringB,
            r.text,
            tag,
            ['replace'],
            textChange,
            otherInfo)


""" Main diff Function used to diff two elements"""


def isSameNode(a, b, isLeaf, outputDict):
    output = {}
    for attrib in a.attrib:  # Compare values assigned to attributes
        if a.get(attrib) != b.get(attrib):
            if b.get(attrib) is not None:
                reportStringChange(
                    outputDict,
                    a.get(attrib),
                    b.get(attrib),
                    a.tag,
                    "ATTRIBUTE VALUE CHANGE")
            else:
                output['afterText'] = ""
                output['rawChange'] = a.get(attrib)
                output['elementType'] = a.tag
                output['op'] = ""
                output['fullText'] = ""
                output['otherInfo'] = "DELETED ATTRIBUTE"
                outputDict[getDiffOutputNumber(outputDict)] = output
    for attrib in b.attrib:
        if a.get(attrib) is None:
            output['afterText'] = b.get(attrib)
            output['rawChange'] = ""
            output['elementType'] = a.tag
            output['op'] = ""
            output['fullText'] = ""
            output['otherInfo'] = "ADDED ATTRIBUTE"
            outputDict[getDiffOutputNumber(outputDict)] = output
    if isLeaf and a.text != b.text:  # Compare text inside element
        reportStringChange(outputDict, a.text, b.text, a.tag, "TEXT CHANGE")
    # if tagsame==True:
        # if a.tag != b.tag:
        # return False
    # if a.prefix != b.prefix:
        # return False
    # if a.tail != b.tail:
        # return False
    # if a.values()!=b.values(): #redundant to the attrib matching
        # return False
    # if sorted(a.keys()) != sorted(b.keys()): #may also be redundant to the attrib matching, #See if any attributes were added/removed
    #    str1 = ''.join(sorted(a.keys()))
    #    str2 = ''.join(sorted(b.keys()))
    #    reportStringChange(str1, str2, a.tag, "ATTRIBUTE CHANGE")


def storeDict(path, outputdict):
    if not os.path.exists(path):
        os.makedirs(path)
    for key in outputdict:
        for key2 in outputdict[key]:
            try:
                # print path+key+key2;
                f = open(path + key + key2 + '.json', 'a')
                json.dump(outputdict[key][key2], f)
                f.close()
            except Exception:
                os.remove(path + key + key2 + '.json')
    return

""" Function to detect similartiy between two strings """
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

""" Returns a portion of a dictionary matching a prefix, s """
def slicedict(d, s):
    return {k: v for k, v in d.iteritems() if k.startswith(s)}

""" Remove un-needed chars from a string """
def removeExtraChars(string1):
    return string1.replace("&#13;", "")


def findSimilarNodes(originalFileHash, newFileHash):
    originalSet = set(originalFileHash)
    newSet = set(newFileHash)
    checkedKeys = []
    for originalFileKey, originalFileValue in originalFileHash.iteritems(
    ):  # Cycle through all original keys
        myMax = 0
        maxNode = None
        maxKey = None
        didFindSimilarMatch = False

        if "li_1" in originalFileKey:
            g = originalFileHash[originalFileKey]
            myMax = 0

        if "/!!/" in originalFileKey:
            start = originalFileKey.rfind("/!!/")
            finish = originalFileKey.rfind("/!/")
            path = originalFileKey[:finish + 4]
        else:
            path = originalFileKey

        if "!!/body/" in path or "!!/head/!" in path:
            matchingSubset = slicedict(newFileHash, path)
        else:
            print "skipped path -- %s", path
            continue

        elementString1 = removeExtraChars(
            etree.tostring(originalFileHash[originalFileKey]))
        for newFileKey in matchingSubset:  # Cycle through all new keys
            if newFileKey in checkedKeys:
                continue
            elementString2 = removeExtraChars(
                etree.tostring(newFileHash[newFileKey]))
            temp = similar(elementString1, elementString2)
            if temp > myMax:
                myMax = temp
                maxNode = newFileHash[newFileKey]
                maxKey = newFileKey
                didFindSimilarMatch = True
                if myMax == 1:
                    checkedKeys.append(originalFileKey)
                    break

        if didFindSimilarMatch:
            if originalFileKey == maxKey:
                continue
            elif originalFileKey in newFileHash:
                tempNode = newFileHash[originalFileKey]
                newFileHash[originalFileKey] = maxNode
                newFileHash[maxKey] = tempNode
            else:
                newFileHash[originalFileKey] = maxNode
    return checkedKeys

""" Reports the number of changes found """
def getDiffOutputNumber(diffHash):
    return len(diffHash)

""" Main differ function """
def htmldiff(path1, path2):
    tree1 = parse(path1).getroot()
    tree2 = parse(path2).getroot()

    elementsA_hash = {}
    elementsB_hash = {}
    isLeafNodeA = {}
    isLeafNodeB = {}
    outputDict = {}
    numberOfChanges = 0

    hashNodes(tree1, elementsA_hash, isLeafNodeA, False, None)
    hashNodes(tree2, elementsB_hash, isLeafNodeB, True, elementsA_hash)
    sameKeys = findSimilarNodes(elementsA_hash, elementsB_hash)

    for key, value in elementsA_hash.iteritems():
        output = {}
        try:
            if key in sameKeys:
                continue

            isSameNode(
                elementsA_hash[key],
                elementsB_hash[key],
                isLeafNodeA[key],
                outputDict)
        except KeyError as e:
            node = elementsA_hash[key]
            # print 'I got a KeyError - reason "%s"' % str(e)
            output['afterText'] = ""
            output['afterAttribute'] = ""
            output['rawTextChange'] = node.text
            output['rawAttributeChange'] = node.attrib
            output['elementType'] = node.tag
            output['op'] = ""
            output['fullText'] = ""
            output['otherInfo'] = "DELETED NODE"
            outputDict[getDiffOutputNumber(outputDict)] = output

    for key, value in elementsB_hash.iteritems():
        output = {}
        try:
            # Check to see if this node exist in the original file
            tempNode = elementsA_hash[key]
        except KeyError as e:
            node = elementsB_hash[key]
            # print 'I got a KeyError - reason "%s"' % str(e)
            output['afterText'] = node.text
            output['afterAttribute'] = node.attrib
            output['rawTextChange'] = node.text
            output['rawAttributeChange'] = node.attrib
            output['elementType'] = node.tag
            output['op'] = ""
            output['fullText'] = ""
            output['otherInfo'] = "ADDED NODE"
            outputDict[getDiffOutputNumber(outputDict)] = output

    print getDiffOutputNumber(outputDict)
    return outputDict

if __name__ == "__main__":
    import sys
    from pprint import *
    if len(sys.argv) == 3:
        f1 = sys.argv[1]
        f2 = sys.argv[2]
        diff = htmldiff(f1, f2)
        pprint(diff)
    elif len(sys.argv) == 2:
        f1 = sys.argv[1] + '/before.html'
        f2 = sys.argv[1] + '/after.html'
        diff = htmldiff(f1, f2)
        pprint(diff)

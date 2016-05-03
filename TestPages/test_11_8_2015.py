#DIFF v1.5
from lxml import etree
from lxml.html.soupparser import parse, fromstring
import requests
import xml.etree.ElementTree as ET
import difflib
from BeautifulSoup import BeautifulSoup
import sys

def makeChildNamesUnique(node):
    children = node.getchildren()
    uniqueSet = {}
    for child in children:
        if child.tag in uniqueSet: #Make every child tag unique
           i = 1
           while True:
              tempkey = '%s_%d' % (child.tag,i)
              if tempkey in uniqueSet:   #Have we seen this tag already
                 i = i + 1
                 continue
              else:  #No,so add it to the set
                 try:
                    child.tag = tempkey
                    break
                 except AttributeError: #Catches immutable nodes
                    print "%s is immutable so please analyze this by hand...most likely a commant" % child.tag
                    #print child.text
                    #node.child.a = (tempkey)
                 
                 uniqueSet[tempkey] = child.tag
                 break
        else: #Its not in the set so add it
           uniqueSet[child.tag] = child.tag
    return node


""" Recursive function used to create a hash map of all the leaf
    nodes in an html file"""
def hashNodes(tree,data,isleaf):
   for node in tree:
      if node.getchildren():  #if true, not a leaf
        hashSingleNode(node, data, isleaf, 0)
        node = makeChildNamesUnique(node)

        #Recursive call to go deeper into the tree
        hashNodes(node,data, isleaf)
      else: #This node must be a leaf node
        hashSingleNode(node, data, isleaf, 1)


def hashSingleNode(node, data, isleaf, mark):
  key = node.tag
  if node.getparent():
    parent_node = node.getparent()
    tempKey = parent_node.tag
    while parent_node.getparent():
        parent_node = parent_node.getparent()
        tempKey = parent_node.tag + '_' + tempKey
    key = '%s_%s' % (tempKey, key)
  if key in data:                      #Handles duplicate paths like 2 scripts inside a body tag
    i = 1
    while True:
       tempkey = '%s_%d' % (key,i)
       if tempkey in data:
          i = i + 1
          continue
       else:
          key = tempkey
          data[key] = node #Put element in hashmap
          if mark == 1:
            isleaf[key] = True #This tag belongs to a leaf node
          else:
            isleaf[key] = False #This tag belongs to a parent node
          break
  else:
    data[key] = node  
    if mark == 1:
      isleaf[key] = True 
    else:
      isleaf[key] = False

""" Function used to print out any changes"""
def reportChange(afterText, rawChange, elementType, listOfStringOperations, fullText, otherInfo=""):
    global noofchanges
    for op in listOfStringOperations:
       noofchanges=noofchanges+1
       print "%s, %s, %s, %s, %s, %s" % (afterText, rawChange, elementType, op, fullText, otherInfo)

""" Online Function I found to find changes between two strings and output it with tags"""
def show_diff(seqm):
    """Unify operations between two compared strings
       seqm is a difflib.SequenceMatcher instance whose a & b are strings"""
    output= []
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
            raise RuntimeError, "unexpected opcode"
    return ''.join(output)

""" Function to elegantly report and text mismatches"""
def reportStringChange(stringA, stringB, tag, otherInfo=""):
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
      reportChange(stringB,i.text,tag, ['ins'],textChange, otherInfo)
   for d in deleteTags:
      reportChange(stringB,d.text,tag, ['del'],textChange, otherInfo)
   for r in replaceTags:
      reportChange(stringB,r.text,tag, ['replace'],textChange, otherInfo)

""" Main diff Function used to diff two elements"""
#TODO figure out what to do when a new attribute is added or is removed
def isSameNode(a,b,isleaf):
    global noofchanges
    for attrib in a.attrib: #Compare values assigned to attributes
        if a.get(attrib) != b.get(attrib):
           if b.get(attrib) is not None:
	      
              reportStringChange(a.get(attrib), b.get(attrib), a.tag, "ATTRIBUTE VALUE CHANGE")
           else:
	      noofchanges=noofchanges+1
              print "%s, %s, %s, %s, %s, %s" % ("", a.get(attrib), a.tag, "", "", "DELETED ATTRIBUTE")
    for attrib in b.attrib: #Maybe delete this code
           if a.get(attrib) is None:
	      noofchanges=noofchanges+1
              print "%s, %s, %s, %s, %s, %s" % (b.get(attrib),"", a.tag, "", "", "ADDED ATTRIBUTE")
    if  isleaf == True and a.text != b.text: #Compare text inside element
        reportStringChange(a.text, b.text, a.tag, "TEXT CHANGE")
    #if tagsame==True:
        #if a.tag != b.tag:
            #return False
    #if a.prefix != b.prefix:
        #return False
    #if a.tail != b.tail:
        #return False
    #if a.values()!=b.values(): #redundant to the attrib matching
       #return False
    # if sorted(a.keys()) != sorted(b.keys()): #may also be redundant to the attrib matching, #See if any attributes were added/removed
    #    str1 = ''.join(sorted(a.keys()))
    #    str2 = ''.join(sorted(b.keys()))
    #    reportStringChange(str1, str2, a.tag, "ATTRIBUTE CHANGE")        
    return True

path1 = sys.argv[1];
path2 = sys.argv[2];
             
tree1 = parse(path1).getroot();
tree2 = parse(path2).getroot();

elementsA_hash = {}
elementsB_hash = {}
isLeafNodeA = {}
isLeafNodeB = {}

hashNodes(tree1,elementsA_hash,isLeafNodeA)
hashNodes(tree2,elementsB_hash,isLeafNodeB)

noofchanges=0

for key,value in elementsA_hash.iteritems():
    try:
       isSameNode(elementsA_hash[key], elementsB_hash[key], isLeafNodeA[key])
    except KeyError, e:
       node = elementsA_hash[key]
       noofchanges=noofchanges+1
       #print 'I got a KeyError - reason "%s"' % str(e)
       print "%s, %s, %s, %s, %s, %s" % ("",node.text,node.tag,"","","DELETED NODE")

for key,value in elementsB_hash.iteritems():
    try:
       tempNode = elementsA_hash[key] #Check to see if this node exist in the original file
    except KeyError, e:
       node = elementsB_hash[key]
       noofchanges=noofchanges+1
       #print 'I got a KeyError - reason "%s"' % str(e)
       print "%s, %s, %s, %s, %s, %s" % (node.text,"",node.tag,"","","ADDED NODE")

print noofchanges

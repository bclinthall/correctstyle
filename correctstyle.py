#! /usr/bin/python2.7


import re
import sys
import os

correctstyleDirName = '.correctstyle'
patterns = [
    #space around patterns
    ('([^/* ])\*([^/=* ])',         r'\1 * \2'),

    # space before patterns
    ('([^+ ])\+(?!\+)',            r'\1 +'), 
    ('([^- ])-(?![->])',           r'\1 -'),
    ('([^ ])\*=',                  r'\1 *='),
    ('([^/* ])/(?![/*])',          r'\1 /'),
    ('([^-+=><!*/ ])=',            r'\1 ='), 
    ('([^ <])<',                   r'\1 <'),
    ('([^->h ])>([^\n])',          r'\1 >\2'),
    ('\}else\b',                   r'} else'),

    # space after patterns
    ('\+([^+=; ]\))',              r'+ \1'),
    ('-([^-=; ]\))',               r'- \1'),
    ('\*=([^ ])',                   r'*= \1'),
    ('/([^/*=\n ])',               r'/ \1'),
    ('=([^= ])',                   r'= \1'),
    ('(?<!-)>([^=>\n ])',          r'> \1'),
    ('(?<!#include )<([^=< ])',    r'< \1'),
    ('\bif\(',                     r'if ('),
    ('\bfor\(',                    r'for ('),
    ('\bwhile\(',                  r'while ('),
    ('\belse\{',                   r'else {'),
    ('\bdo\{',                     r'do {'),

    # curly rules
    ('\n\s*\{',                    r' {'),
    ('\}\n\s*else',                r'} else')
]

def toIgnoreRecord(contextBefore, contextAfter):
    ignoreRecord = contextBefore + "<*before::after*>" + contextAfter
    ignoreRecord = ignoreRecord.replace("\n", "<*br*>")
    return ignoreRecord + "\n"

def makeIgnoreFileName(fileName):
    global correctstyleDirName
    return correctstyleDirName + os.path.sep + fileName

def writeIgnore(fileName, contextBefore, contextAfter):
    global correctstyleDirName
    if not os.path.exists(correctstyleDirName):
        os.makedirs(correctstyleDirName)
    ignoreFileName = makeIgnoreFileName(fileName) 
    ignoreRecord = toIgnoreRecord(contextBefore, contextAfter)
    with open(ignoreFileName, "a") as f:
        f.write(ignoreRecord)
        

def isIgnored(fileName, contextBefore, contextAfter):
    global correctstyleDirName
    if not os.path.exists(correctstyleDirName):
        return False
    ignoreFileName = makeIgnoreFileName(fileName)
    if not os.path.exists(ignoreFileName):
        return False
    ignoreRecord = toIgnoreRecord(contextBefore, contextAfter)
    with open(ignoreFileName, "r") as f:
        for line in f:
            if line == ignoreRecord:
                return True
    return False
                
    
def getContext(txt, match):
    beginContext = txt.rfind('\n', 0, match.start())
    endContext = txt.find('\n', match.end())
    return txt[beginContext+1 : endContext]
    
def splice(txt, insert, start, end):
    return txt[:start] + insert + txt[end:]


def correctByPattern(fileName, txt, pattern, replacement):
    pos = 0
    match = pattern.search(txt, pos)
    while match:
        before = match.group(0)
        after = re.sub(pattern, replacement, before) 

        contextBefore = getContext(txt, match)
        contextMatch = pattern.search(contextBefore)
        contextAfter = splice(contextBefore, after, contextMatch.start(), contextMatch.end())
        if not isIgnored(fileName, contextBefore, contextAfter):
            lineNo = txt.count("\n", 0, match.start()) + 1
            print   "\n<<<<<<<<<< %s: %d     '%s'  :  '%s'" % (fileName, lineNo, pattern.pattern, replacement)
            print "%s\n==========\n%s" % (contextBefore, contextAfter)
            doIt = raw_input(">>>>>>>>>> make this replacement? [yes] or no:  ")
            doIt = len(doIt) == 0 or doIt[0] != 'n' and doIt[0] != 'N'
            if doIt:
                print "replacement made"
                txt = splice(txt, after, match.start(), match.end())
                pos = match.start()
            else:
                writeIgnore(fileName, contextBefore, contextAfter)
                pos = match.end()
        else:
            pos = match.end()
        match = pattern.search(txt, pos)
    return txt


def correctFile(fileName):
    with open(fileName, "r") as mFile:
        txt = mFile.read();

    for pattern, replacement in patterns:
        txt  = correctByPattern(fileName, txt, re.compile(pattern), replacement)

    with open(fileName, "w") as mFile:
        mFile.write(txt);
    
    print "correctstyle finished with " + fileName

for fileName in sys.argv[1:]:
    correctFile(fileName)


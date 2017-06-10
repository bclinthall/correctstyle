#! /usr/bin/python2.7

# Run correctstyle.py from command line to offer corrections for common style inconsistencies in C family languages (C, C++, Java, etc)
# 
# Copyright (C) 2017  B. Clint Hall
#
# B. Clint Hall
# contact by creating a github issue  https://github.com/bclinthall/correctstyle/
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
import sys
import os

usage = "usage: correctstyle.py file ..."
warranty = '''
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

conditions = '''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. see <http://www.gnu.org/licenses/>.
'''

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
    ('(?<!-)>([^=>\n ])',          r'> \1'), ('(?<!#include )<([^=< ])',    r'< \1'),
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

def promptForReplacement(fileName, lineNo, pattern, replacement, contextBefore, contextAfter):
    print   "\n<<<<<<<<<< %s: %d     '%s'  :  '%s'" % (fileName, lineNo, pattern.pattern, replacement)
    print "%s\n==========\n%s" % (contextBefore, contextAfter)
    doIt = raw_input(">>>>>>>>>> make this replacement? [yes] or no:  ")
    if doIt == 'show w':
        print warranty
        return promptForReplacement(fileName, lineNo, pattern, replacement, contextBefore, contextAfter)
    elif doIt == 'show c':
        print conditions
        return promptForReplacement(fileName, lineNo, pattern, replacement, contextBefore, contextAfter)
    else:
        return len(doIt) == 0 or doIt[0] != 'n' and doIt[0] != 'N'

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
            doIt = promptForReplacement(fileName, lineNo, pattern, replacement, contextBefore, contextAfter)
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

print "correctstyle Copyright (C) 2017 B. Clint Hall"
print "This program comes with ABSOLUTELY NO WARRANTY; for details call `correctstyle.py -w'."
print "This is free software, and you are welcome to redistribute it under certain conditions; call `correctstyle.py -c' for details."

if len(sys.argv) == 1:
    print usage
for fileName in sys.argv[1:]:
    if fileName[0] == '-':
        if fileName[1] == 'w':
            print warranty
        elif fileName[1] == 'c':
            print conditions
        else:
            print usage
    else:
        correctFile(fileName)


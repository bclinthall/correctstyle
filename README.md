# correctstyle

Run from command line. correctstyle will offer corrections for common style inconsistencies in C family languages (C, C++, Java, etc)

```usage: correctstyle.py file ...```

## Patterns
Adjust the `patterns` list in `correctstyle.py` to suit your own preferences.

## Accept/Decline
Each correction can be accepted or declined because you probably want spaces around the `-` in `7-3` but not in `64-bit`. 

## Ignoring
Once you've declined a particular correction in a particular file, you won't be asked about it again.
correctstyle.py accomplishes this by storing the text around the proposed correction with and without the proposed correction.  So, if you modify the context of a proposed correction, you will be prompted for it again.  The data is kept in a `.correctstyle` subdirectory in your working directory.

#
#   Module:     Textfile
#   Platform:   Python 3
#
#   Utility functions for working with text files.
#
#   Copyright Craig Farrow, 2019
#


from random import randint
import re


LINECOMMENTS = "#;"

def randomLine(f):
    """
    Given a text file return a random line, ignoring blank lines
    and those starting with "#" or ";".

    f -- the handle for an open text file.
    """
    def __filterLines(s):
        if not s.strip():
            return False
        if s[0] in LINECOMMENTS:
            return False
        return True

    f.seek(0)
    lines = list(filter(__filterLines, f.readlines()))
    n = len(lines)
    i = randint(0,n-1)
    return lines[i].strip("\n")


def randomSection(f):
    """
    Given a text file divided into sections by the '#' character,
    return a random section.

    f -- the handle for an open text file.
    """
    
    f.seek(0)
    sections = re.findall("[^#]+", f.read())
    n = len(sections)
    i = randint(0,n-1)
    return sections[i].strip("\n")
 
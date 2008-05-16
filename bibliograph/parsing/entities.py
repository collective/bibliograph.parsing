#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Modul:          Entities
    Description:    Entitify and Deentitfy Specialchars for html/xml
    Version:        0.2
    Copyright:      2004 by Fritz Cizmarov fritz@sol.at
    Created:        29. Jul. 2004
    Last modified:  29. Jul. 2004
    License:        free
    Requirements:   Python2.3
    Exports:        Entities, entitify, deentitify
"""
"""
    2005.09.08: Adapted to CMFBib's needs (Raphael)
"""

import re
import sys
from array import array
from htmlentitydefs import name2codepoint, codepoint2name

_c2n = {34 : "quot", 38 : "amp", 39 : "apos", 60 : "lt", 62 : "gt"}
_n2c = {"quot" : 34, "amp" : 38, "apos" : 39, "lt" : 60, "gt" : 62}

_regex = re.compile(r"&([#\w]+);", flags=re.UNICODE) # find entities


class Entities(object):
    """ Pseudomapping of entities """

    __slots__ = ["n2c","ukh"]

    def __init__(self, n2c={}, handle_unknown=lambda key: u"&%s;" % key ):
        super(Entities, self).__init__()
        self.n2c = n2c
        self.ukh = handle_unknown # standart restore entity

    def __getitem__(self, key):
        """ calculate unicode or get it from n2c """
        if key[0] == "#":   # numeric value
            if key[1] in "xX":  # hexadecimal
                return unichr(int(key[2:], 16))
            else:               # decimal
                return unichr(int(key[1:]))
        else: # named Entity
            try:
                return unichr(self.n2c[key])
            except KeyError:
                return self.ukh(key)


def entitify(ustring, c2n=_c2n):
    """ convert unicodestring to string with entities """
    tmp = array('c')
    if not isinstance(ustring, unicode):
        raise TypeError ("argument must be unicode")
    for char in ustring:
        cc = ord(char)
        if ( not (32 <= cc <= 127)) or c2n.has_key(cc):
            tmp.fromstring("&%s;" % c2n.get(cc, "#x%x" % cc))
        else: # simple ascii and not specialchar
            tmp.append(chr(cc))
    return tmp.tostring()


def deentitify(string, n2c=_n2c):
    """ convert string with entities to unicodestring """
    return _regex.sub(r"%(\1)s", string) % Entities(n2c)

class Convert:
    """Wrapper class for the entity module"""
    def deentitify(self, string, n2c=_n2c):
        return deentitify(string, n2c=_n2c)
    def entitify(self, ustring, c2n=_c2n):
        entitify(ustring, c2n=_c2n)
    def __call__(self, string=''):
        if _regex.search(string): # has entities?
            return deentitify(string, name2codepoint)
        else:
            return entitify(string.decode(sys.getfilesystemencoding()),
                            codepoint2name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: %s <string>"
        sys.exit()
    string = sys.argv[1]
    if _regex.search(string): # has entities?
        print deentitify(string, name2codepoint)
    else:
        print entitify(string.decode(sys.getfilesystemencoding()),
                       codepoint2name)


import unittest
import codecs
from zope.interface import implements
from bibliograph.core.interfaces import IBibliographicReference


ENCODING = 'utf-8'

class BaseParserTestCase(unittest.TestCase):

    def readFile(self, path, encoding=ENCODING):
        out = codecs.open(path, 'r', ENCODING).read()
        out = out.lstrip( unicode( codecs.BOM_UTF8, "utf8" ) )
        out = out.replace('\r\n', '\n').replace('\r', '\n')
        return out

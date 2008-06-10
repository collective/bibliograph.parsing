import unittest
from zope.interface.verify import verifyObject

from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.base import BibliographyParser


class BibliographyParserTest(unittest.TestCase):
    '''Tests for the parser base class'''

    def test_init(self):
        self.failUnless(BibliographyParser())

    def test_provides(self):
        self.failUnless(IBibliographyParser.providedBy(BibliographyParser()))

    def test_verify(self):
        self.failUnless(verifyObject(IBibliographyParser, BibliographyParser()))

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(BibliographyParserTest),])
    return suite

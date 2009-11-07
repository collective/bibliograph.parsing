import unittest

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.interface.verify import verifyObject

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import BaseParserTestCase
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.ris import RISParser


class TestRISParser(BaseParserTestCase):
    """tests to cover the RIS parser"""

    def setUp(self):
        setUp()
        from bibliograph.rendering.interfaces import IBibTransformUtility
        from bibliograph.rendering.utility import ExternalTransformUtility    
        ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                             name=u'external')
        self.parser = RISParser()

    def tearDown(self):
        tearDown()

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(RISParser()))
        self.failUnless(verifyObject(IBibliographyParser, RISParser()))
    
    def test_Parser(self):
        """test the functioning of the parser"""
        if self.parser.isAvailable():
            source = self.readFile(setup.RIS_SOURCE)
            self.failUnless(source)
            entries = self.parser.getEntries(source)
            self.failUnless( len(entries) == 7 )
            entry = entries[0]
            t1 = u'Markets and Municipalities: A Study of the Behavior of the Danish Municipalities'
            self.failUnless( entry.title == t1 )
            self.failUnless( entry.pages == '79--102' )
            self.failUnless( entry.volume == '114' )
            self.failUnless( entry.issue == '1 - 2' )
            self.failUnless( entry.publication_year == '2003' )
            self.failUnless( entry.journal == 'Public Choice' )
            self.failUnless( entry.publication_month == 'Jan' )
            self.failUnless( len(entry.authors) == 2 )
            self.failUnless( entry.authors[0].lastname == u'Christoffersen' )
            self.failUnless( entry.authors[0].firstname == u'Henrik' )
            self.failUnless( entry.authors[0].middlename == u'' )
            self.failUnless( entry.authors[1].lastname == u'Paldam' )
            self.failUnless( entry.authors[1].firstname == u'Martin' )
            self.failUnless( entry.authors[1].middlename == u'' )
        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
            
    def test_FormatDetection(self):
        s1 = self.readFile(setup.RIS_SOURCE)
        s2 = self.readFile(setup.ENDNOTE_TEST_SOURCE)
        self.failUnless(self.parser.checkFormat(s1),
                        'RIS Parser failed to detect RIS format')
        self.failIf(self.parser.checkFormat(s2),
                    'RIS Parser incorrectly detected EndNote format as RIS')
    

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestRISParser),])
    return suite

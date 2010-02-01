import unittest

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.interface.verify import verifyObject

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.ris import RISParser

class testRISParser(unittest.TestCase):
    """tests to cover the RIS parser"""

    def setUp(self):
        setUp()
        from bibliograph.rendering.interfaces import IBibTransformUtility
        from bibliograph.rendering.utility import ExternalTransformUtility
        ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                             name=u'external')

    def tearDown(self):
        tearDown()

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(RISParser()))
        self.failUnless(verifyObject(IBibliographyParser, RISParser()))

    def test_Parser(self):
        """test the functioning of the parser"""
        parser = RISParser()
        if parser.isAvailable():
            source = open(setup.RIS_SOURCE, 'r').read()
            self.failUnless(source)

            entries = TestEntries(parser.getEntries(source))
            self.failUnless( len(entries) == 7 )
            self.failUnless( 'Markets and Municipalities: A Study of the Behavior of the Danish Municipalities' in entries.titles())

            entry = entries.entries[0]
            self.failUnless( entry.pages == '79--102' )
            self.failUnless( entry.volume == '114' )
            self.failUnless( entry.number == '1 - 2' )
            self.failUnless( entry.publication_year == '2003' )
            self.failUnless( entry.journal == 'Public Choice' )
            # XXX This test could be adjusted if the parser got smarter about
            #     about converting 'Mar.' into 'March'
            ## rr: which it did inbetween it seems because I had to add
            ## the fully spelled out month names to the 'month_mapper' dict.
            self.failUnless( entry.publication_month == '01' )

            entry_authors = entries.entries[0].authors
            self.failUnless( len( entry_authors ) == 2 )
            self.failUnless( entry_authors[0]['lastname'] == 'Christoffersen' )
            self.failUnless( entry_authors[0]['firstname'] == 'Henrik' )
            self.failUnless( entry_authors[0]['middlename'] == '' )
            self.failUnless( entry_authors[1]['lastname'] == 'Paldam' )
            self.failUnless( entry_authors[1]['firstname'] == 'Martin' )
            self.failUnless( entry_authors[1]['middlename'] == '' )

            last_entry = entries.entries[-1]
            self.assertEqual(last_entry.authors[1]['lastname'], u'M\xfcller'.encode('utf-8'))

        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"

    def test_FormatDetection(self):
        parser = RISParser()

        s1 = open(setup.RIS_SOURCE, 'r').read()
        s2 = open(setup.ENDNOTE_TEST_SOURCE, 'r').read()

        self.failUnless(parser.checkFormat(s1), 'RIS Parser failed to detect RIS format')
        self.failIf(parser.checkFormat(s2), 'RIS Parser incorrectly detected EndNote format as RIS')


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(testRISParser),])
    return suite

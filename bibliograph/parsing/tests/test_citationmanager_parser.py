import unittest

from zope.interface.verify import verifyObject

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.citationmanager import CitationManagerParser

class TestCitationManagerParser(unittest.TestCase):
    ""

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(CitationManagerParser()))
        self.failUnless(verifyObject(IBibliographyParser, CitationManagerParser()))

    def test_parser(self):
        source = open(setup.CITATION_MANAGER_SOURCE, 'r').read()
        self.failUnless(source)
        
        p = CitationManagerParser()
        entries = TestEntries(p.getEntries(source))
        
        self.failUnless( len(entries) == 3 )
        self.failUnless( 'Transfers in Kind: Why They Can be Efficient and Nonpaternalistic' in entries.titles())
        self.failUnless( entries.entries[0].pages == '1345-1351' )
        self.failUnless( len( entries.entries[0].authors ) == 2 )
        
        entry1authors = entries.entries[1].authors
        self.failUnless( entry1authors[0]['lastname'] == 'Murphy' )
        self.failUnless( entry1authors[0]['firstname'] == 'Kevin' )
        self.failUnless( entry1authors[0]['middlename'] == 'M.' )
        self.failUnless( entry1authors[1]['lastname'] == 'Shleifer' )
        self.failUnless( entry1authors[1]['firstname'] == 'Andrei' )
        self.failUnless( entry1authors[1]['middlename'] == '' )
        self.failUnless( entry1authors[2]['lastname'] == 'Vishny' )
        self.failUnless( entry1authors[2]['firstname'] == 'Robert' )
        self.failUnless( entry1authors[2]['middlename'] == 'W.' )

        entry2 = entries.entries[2]
        self.failUnless( entry2.volume == '57' )
        self.failUnless( entry2.number == '1' )
        self.failUnless( entry2.publication_year == '1967' )
        # XXX This test could be adjusted if the parser got smarter about
        #     about converting 'Mar.' into 'March'
        self.failUnless( entry2.publication_month == 'Mar.' )
    

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestCitationManagerParser),])
    return suite

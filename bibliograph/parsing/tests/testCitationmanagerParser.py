import unittest

from bibliograph.parsing.tests import setup

from bibliograph.parsing.parsers.citationmanager import CitationManagerParser

class testCitationManagerParser(unittest.TestCase):
    ""

    def test_Parser(self):
        source = open(setup.CITATION_MANAGER_SOURCE, 'r').read()
        p = CitationManagerParser()
        entries = p.getEntries(source)
        
        self.failUnless( len(entries) == 3 )
        self.failUnless( entries[0]['title'] == 'Transfers in Kind: Why They Can be Efficient and Nonpaternalistic' )
        self.failUnless( entries[0]['pages'] == '1345-1351' )
        self.failUnless( len( entries[0]['authors'] ) == 2 )
        self.failUnless( entries[1]['authors'][0]['lastname'] == 'Murphy' )
        self.failUnless( entries[1]['authors'][0]['firstname'] == 'Kevin' )
        self.failUnless( entries[1]['authors'][0]['middlename'] == 'M.' )
        self.failUnless( entries[1]['authors'][1]['lastname'] == 'Shleifer' )
        self.failUnless( entries[1]['authors'][1]['firstname'] == 'Andrei' )
        self.failUnless( entries[1]['authors'][1]['middlename'] == '' )
        self.failUnless( entries[1]['authors'][2]['lastname'] == 'Vishny' )
        self.failUnless( entries[1]['authors'][2]['firstname'] == 'Robert' )
        self.failUnless( entries[1]['authors'][2]['middlename'] == 'W.' )
        self.failUnless( entries[2]['volume'] == '57' )
        self.failUnless( entries[2]['number'] == '1' )
        self.failUnless( entries[2]['publication_year'] == '1967' )
        # XXX This test could be adjusted if the parser got smarter about
        #     about converting 'Mar.' into 'March'
        self.failUnless( entries[2]['publication_month'] == 'Mar.' )
    

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(testCitationManagerParser),])
    return suite
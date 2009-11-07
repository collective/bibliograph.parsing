import unittest
from zope.interface.verify import verifyObject

from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IArticleReference

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import BaseParserTestCase
from bibliograph.parsing.parsers.medline import MedlineParser
from bibliograph.parsing.interfaces import IBibliographyParser

class TestMedlineParser(BaseParserTestCase):

    def setUp(self):
        self.parser = MedlineParser()

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(self.parser))
        self.failUnless(verifyObject(IBibliographyParser, self.parser))

    def test_import(self):
        source = self.readFile(setup.MEDLINE_TEST_MED)
        self.failUnless(source)
        entries = self.parser.getEntries(source)
        self.failUnless( len(entries) == 4 )
        for each in entries:
            self.failUnless( IBibliographicReference.providedBy(each) )
        t1 = u'Molecular genetic evidence for parthenogenesis in the Burmese python, Python molurus bivittatus.'
        self.failUnless( entries[0].title == t1 )
        self.failUnless( len(entries[0].authors) == 3 )
        self.failUnless( entries[0].authors[0].lastname == u'Groot' )
        self.failUnless( entries[0].authors[0].firstname == u'T' )
        self.failUnless( entries[0].authors[0].middlename == u'V M' )
        self.failUnless( entries[1].getIdentifierById('pmid') == u'12616573' )
        self.failUnless( IArticleReference.providedBy(entries[1]) )
        
    def test_check_format(self):
        s0 = self.readFile(setup.MEDLINE_TEST_MED)
        s1 = self.readFile(setup.RIS_SOURCE)
        s3 = self.readFile(setup.ENDNOTE_TEST_SOURCE)
        self.failUnless(self.parser.checkFormat("AB  -\nAU  -\nPMID-\nTI  -"))
        self.failUnless(self.parser.checkFormat(s0), 
                        'Medline Parser failed to detect Medline format')
        self.failIf(self.parser.checkFormat(s1), 
                        'Medline Parser incorrectly accepted RIS format')
        self.failIf(self.parser.checkFormat(s3), 
                    'Medline Parser incorrectly accepted EndNote format')

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestMedlineParser),])
    return suite

import unittest

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.interface.verify import verifyObject

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import BaseParserTestCase
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.xml import XMLParser


class TestXMLParser(BaseParserTestCase):
    """tests to cover the XML parser"""

    def setUp(self):
        setUp()
        from bibliograph.rendering.interfaces import IBibTransformUtility
        from bibliograph.rendering.utility import ExternalTransformUtility    
        ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                             name=u'external')
        self.parser = XMLParser()

    def tearDown(self):
        tearDown()

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(XMLParser()))
        self.failUnless(verifyObject(IBibliographyParser, XMLParser()))
    
    def test_Parser(self):
        """test the functioning of the parser"""
        if self.parser.isAvailable():
            source = self.readFile(setup.MEDLINE_TEST_XML)
            self.failUnless(source)
            entries = self.parser.getEntries(source)
            # are there enough entries?
            self.failUnless( len(entries) == 4 )
            # test individual name parsings:
            #  lastname, one initial
            self.failUnless( len(entries[0].authors) == 3 )
            self.failUnless( entries[0].authors[0].lastname == u'Groot' )
            self.failUnless( entries[2].authors[1].lastname == u'Hunter' )
            self.failUnless( entries[2].authors[1].middlename == u'P.' )
            t3 = u'Pharmacokinetics and tissue concentrations of azithromycin in ball pythons (Python regius).'
            self.failUnless( entries[2].title == t3 )
        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
            
    def test_FormatDetection(self):
        s1 = self.readFile(setup.MEDLINE_TEST_XML)
        s2 = self.readFile(setup.MEDLINE_TEST_BIB)
        s3 = self.readFile(setup.MEDLINE_TEST_MED)
        self.failUnless(self.parser.checkFormat(s1),
                        'XML Parser failed to detect XML(MODS) format')
        self.failIf(self.parser.checkFormat(s2),
                    'XML Parser incorrectly detected Bibtex format as XML(MODS)')
        self.failIf(self.parser.checkFormat(s3),
                    'XML Parser incorrectly detected Medline format as XML(MODS)')
    

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestXMLParser),])
    return suite
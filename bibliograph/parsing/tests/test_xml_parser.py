import unittest

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.interface.verify import verifyObject

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.xml import XMLParser

class testXMLParser(unittest.TestCase):
    """tests to cover the XML parser"""

    def setUp(self):
        setUp()
        from bibliograph.rendering.interfaces import IBibTransformUtility
        from bibliograph.rendering.utility import ExternalTransformUtility    
        ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                             name=u'external')

    def tearDown(self):
        tearDown()

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(XMLParser()))
        self.failUnless(verifyObject(IBibliographyParser, XMLParser()))
    
    def test_Parser(self):
        """test the functioning of the parser"""
        parser = XMLParser()
        if parser.isAvailable():
            source = open(setup.MEDLINE_TEST_XML, 'r').read()
            self.failUnless(source)
            
            entries = TestEntries(parser.getEntries(source))
            
            # are there enough entries?
            self.failUnless(len(entries) == 4)
            # are there the right number of authors?
            self.failUnless(len(entries.author_last_names()) == 13)
            # test individual name parsings:
            #  lastname, one initial
            this_entry = entries.entryByTitle("Molecular genetic evidence for parthenogenesis in the Burmese python, Python molurus bivittatus.")
            expected_author = {"firstname": "E.", "middlename": "","lastname": "Bruins"}
            self.failUnless(this_entry.authorIsPresent(expected_author), "author: %s is not listed" % expected_author)
            # lastname, more than one initial
            expected_author = {"firstname": "T.", "middlename": "V.M.","lastname": "Groot"}
            self.failUnless(this_entry.authorIsPresent(expected_author), "author: %s is not listed" % expected_author)
            # lastname, firstname, middle initial
            this_entry = entries.entryByTitle("Pharmacokinetics and tissue concentrations of azithromycin in ball pythons (Python regius).")
            expected_author = {"firstname": "Robert", "middlename": "P.","lastname": "Hunter"}
            self.failUnless(this_entry.authorIsPresent(expected_author), "author: %s is not listed" % expected_author)
            
                                
        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
            
    def test_FormatDetection(self):
        parser = XMLParser()
    
        s1 = open(setup.MEDLINE_TEST_XML, 'r').read()
        s2 = open(setup.MEDLINE_TEST_BIB, 'r').read()
        s3 = open(setup.MEDLINE_TEST_MED, 'r').read()
        
        self.failUnless(parser.checkFormat(s1), 'XML Parser failed to detect XML(MODS) format')
        self.failIf(parser.checkFormat(s2), 'XML Parser incorrectly detected Bibtex format as XML(MODS)')
        self.failIf(parser.checkFormat(s3), 'XML Parser incorrectly detected Medline format as XML(MODS)')
    

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(testXMLParser),])
    return suite
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
            print entries
        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
    

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(testXMLParser),])
    return suite
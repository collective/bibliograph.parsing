import unittest
from zope.interface.verify import verifyObject
from zope.app.testing import ztapi

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import BaseParserTestCase
from bibliograph.parsing.parsers.endnote import EndNoteParser
from bibliograph.parsing.interfaces import IBibliographyParser


class TestEndNoteParser(BaseParserTestCase):

    def setUp(self):
        self.parser = EndNoteParser()
        from bibliograph.rendering.interfaces import IBibTransformUtility
        from bibliograph.rendering.utility import ExternalTransformUtility    
        ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                             name=u'external')

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(EndNoteParser()))
        self.failUnless(verifyObject(IBibliographyParser, EndNoteParser()))

    def test_import(self):
        if self.parser.isAvailable():
            source = self.readFile(setup.ENDNOTE_TEST_SOURCE)
            self.failUnless(source)
            entries = self.parser.getEntries(source)
            self.failUnless(len(entries) == 2)
            self.failUnless( len(entries[0].authors) == 4 )
            self.failUnless(entries[0].authors[1].lastname == u'Dufour')
            self.failUnless(entries[0].authors[1].firstname == u'J.')
            self.failUnless(entries[0].authors[1].middlename == u'C.')
            self.failUnless(entries[0].authors[3].lastname == u'Fieschi')
            self.failUnless(entries[0].authors[3].firstname == u'M.')
            self.failUnless(entries[0].authors[3].middlename == u'')
            t0 = u'Combining advanced networked technology and pedagogical methods to improve collaborative distance learning'
            self.failUnless(entries[0].title == t0)
            t1 = u'Collaborative and workflow-oriented digital portfolio: Creating a web-based tool to support a nationwide program of practices evaluation in the blood transfusion area'
            self.failUnless(entries[1].title == t1)
            # Keywords - first entry in sample file has none, second has 9
            # XXX we don't handle keywords in the (bibtex) parser, yet.
            #self.failUnless( len(entries[0].keywords) == 0 )
            #self.failUnless( len(entries[1].keywords) == 9 )
            # Confirm a few w/ tricky characters survived the parse
            kwds = ["Health Services Research/ organization \\& administration",
                    "Primary Health Care/ standards",
                    "Program Evaluation",
                    "Quality Assurance, Health Care"]
            #for keyword in kwds:
            #    self.failUnless(keyword in entries[1].keywords,
            #                    "Failed to correctly parse keyword: '%s'" % keyword)
        else:
            print """\nOne or more transformation tool was not found!
Please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
        
    def test_check_format(self):
        s0 = self.readFile(setup.ENDNOTE_TEST_SOURCE)
        s1 = self.readFile(setup.RIS_SOURCE)
        self.failUnless(self.parser.checkFormat("%0 \n%A \n%D \n%T "))
        self.failIf(self.parser.checkFormat("%0 \n%A \n%T "))
        self.failUnless(self.parser.checkFormat(s0), 
                        'Endnote Parser failed to detect Endnote format')
        self.failIf(self.parser.checkFormat(s1), 
                    'Endnote Parser incorrectly accepted RIS format')

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestEndNoteParser),])
    return suite

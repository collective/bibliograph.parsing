import unittest
from zope.interface.verify import verifyObject
from zope.app.testing import ztapi

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries
from bibliograph.parsing.parsers.endnote import EndNoteParser
from bibliograph.parsing.interfaces import IBibliographyParser

class TestEndNoteParser(unittest.TestCase):

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
            source = open(setup.ENDNOTE_TEST_SOURCE, 'r').read()
            self.failUnless(source)
            entries = TestEntries(self.parser.getEntries(source))
            self.failUnless(len(entries) == 2)
            expected_author_last_names = ('Dufour', 'Fieschi', 'Hergon',
                                          'Joubert', 'Raps', 'Staccini',)

            parsed_author_last_names = entries.author_last_names()
            for name in expected_author_last_names:
                self.failUnless(name in parsed_author_last_names,
                                'Parse failed - missing author %s' % name)

            expected_titles = ('Combining advanced networked technology and pedagogical methods to improve collaborative distance learning',
                               'Collaborative and workflow-oriented digital portfolio: Creating a web-based tool to support a nationwide program of practices evaluation in the blood transfusion area',)
                               
            parsed_titles = [e.title for e in entries.entries]
            for title in expected_titles:
                self.failUnless(title in parsed_titles,
                                'Parse failed - missing expected title "%s"' %
                                title)
            # Keywords - first entry in sample file has none, second has 9
            self.failIf(hasattr(entries.entries[0],'keywords')
                        and entries.entries[0].keywords,
                        'Parsed non existing keywords')
            self.failUnless(len(entries.entries[1].keywords) == 9)
            # Confirm a few w/ tricky characters survived the parse
            kwds = ["Health Services Research/ organization & administration",
                    "Primary Health Care/ standards",
                    "Program Evaluation",
                    "Quality Assurance, Health Care"]
            for keyword in kwds:
                self.failUnless(keyword in entries.entries[1].keywords,
                                "Failed to correctly parse keyword: '%s'" % keyword)
        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
        
    def test_check_format(self):
        s0 = open(setup.ENDNOTE_TEST_SOURCE, 'r').read()
        s1 = open(setup.RIS_SOURCE, 'r').read()
        
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

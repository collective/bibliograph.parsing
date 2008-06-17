import unittest
from zope.interface.verify import verifyObject
from zope.app.testing import ztapi

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries
from bibliograph.parsing.parsers.endnote import EndNoteParser
from bibliograph.parsing.interfaces import IBibliographyParser

class TestEndNoteParser(unittest.TestCase):

    def setUp(self):
        #setUp()
        from bibliograph.rendering.interfaces import IBibTransformUtility
        from bibliograph.rendering.utility import ExternalTransformUtility    
        ztapi.provideUtility(IBibTransformUtility, ExternalTransformUtility(),
                             name=u'external')

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(EndNoteParser()))
        self.failUnless(verifyObject(IBibliographyParser, EndNoteParser()))

    def test_EndNoteImport(self):

        parser = EndNoteParser()
        if parser.isAvailable():
            source = open(setup.ENDNOTE_TEST_SOURCE, 'r').read()
            self.failUnless(source)
            entries = TestEntries(parser.getEntries(source))
            self.failUnless(len(entries) == 2)
            expected_author_last_names = ('Dufour', 'Fieschi', 'Hergon',
                                          'Joubert', 'Raps', 'Staccini',)

            parsed_author_last_names = entries.author_last_names()
            for name in expected_author_last_names:
                self.failUnless(name in parsed_author_last_names,
                                'Parse failed - missing author %s' % name)
        else:
            print """\nOne or more transformationtool was not found!
please make sure bibutils is installed to run all tests. """
            print ("-" * 20) + "\n"
        

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestEndNoteParser),])
    return suite

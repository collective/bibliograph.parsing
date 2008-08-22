import unittest
from zope.interface.verify import verifyObject

from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries
from bibliograph.parsing.parsers.medline import MedlineParser
from bibliograph.parsing.interfaces import IBibliographyParser

class TestMedlineParser(unittest.TestCase):

    def setUp(self):
        self.parser = MedlineParser()

    def test_parser_contract(self):
        self.failUnless(IBibliographyParser.providedBy(self.parser))
        self.failUnless(verifyObject(IBibliographyParser, self.parser))

    def test_import(self):
        source = open(setup.MEDLINE_TEST_MED, 'r').read()
        self.failUnless(source)

        parser = MedlineParser()
        entries = TestEntries(parser.getEntries(source))
        self.failUnless(len(entries) == 4)
        expected_author_last_names = ("Groot","Bruins","Breeuwer","Alibardi",\
                                          "Thompson","Coke","Hunter","Isaza",\
                                          "Koch","Goatley","Carpenter",\
                                          "Trape","Mane",)

        parsed_author_last_names = entries.author_last_names()
        for name in expected_author_last_names:
            self.failUnless(name in parsed_author_last_names,
                            'Parse failed - missing author %s' % name)
        
    def test_check_format(self):
        s0 = open(setup.MEDLINE_TEST_MED, 'r').read()
        s1 = open(setup.RIS_SOURCE, 'r').read()
        s3 = open(setup.ENDNOTE_TEST_SOURCE, 'r').read()
        
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

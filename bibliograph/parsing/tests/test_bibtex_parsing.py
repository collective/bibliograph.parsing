# -*- coding: utf-8 -*-
#######################################################
#                                                     #
#    Copyright (C), 2004, Raphael Ritz                #
#    <r.ritz@biologie.hu-berlin.de>                   #
#                                                     #
#    Humboldt University Berlin                       #
#                                                     #
# Copyright (C), 2005, Logilab S.A. (Paris, FRANCE)   #
# http://www.logilab.fr/ -- mailto:contact@logilab.fr #
#                                                     #
#######################################################
import unittest

from bibliograph.parsing.parsers.bibtex import BibtexParser
from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import TestEntries

class TestBibtexParsing(unittest.TestCase):
    """
    """

    def setUp(self):
        self.parser = BibtexParser()
            
    def testFormatDetection(self):
        source_files = (setup.MEDLINE_TEST_BIB, setup.BIBTEX_TEST_BIB, 
                        setup.IDCOOKING_TEST_BIB, setup.PDFFOLDER_TEST_BIB, 
                        setup.BIBTEX_TEST_BIB_DUP, setup.BIBTEX_TEST_MULTI_AUTHORS,
                        setup.BIBTEX_TEST_INBOOKREFERENCES, setup.BIBTEX_TEST_LASTFIELDKOMMA,
                        setup.BIBTEX_TEST_TYPEFIELD, setup.BIBTEX_TEST_CITE_KEY)
                     
        for source_file in source_files:
            source = open(source_file, 'r').read()
            self.failUnless(self.parser.checkFormat(source), 'BibTeX parser failed to detect BibTeX format in file %s' % source_file)
        
        # check negative detection (check properly rejects non-bibtex format files)
        source = open(setup.MEDLINE_TEST_MED, 'r').read()
        self.failIf(self.parser.checkFormat(source), 'BibTeX parser incorrectly detected BibTeX format in file %s' % setup.MEDLINE_TEST_MED)

    def testBibtexAuthorParsing(self):
        source = open(setup.BIBTEX_TEST_MULTI_AUTHORS, 'r').read()
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)
        heckman =  {'middlename': 'J.',
                    'firstname' : 'James',
                    'lastname'  : 'Heckman'}
        carneiro = {'middlename': '',
                    'firstname' : 'Pedro',
                    'lastname'  : 'Carneiro'}
        self.failUnless( len( result['authors'] ) == 2 )
        author1 = result['authors'][0]
        self.failUnless(author1['middlename'] == carneiro['middlename'])
        self.failUnless(author1['firstname'] == carneiro['firstname'])
        self.failUnless(author1['lastname'] == carneiro['lastname'])
        author2 = result['authors'][1]
        self.failUnless(author2['middlename'] == heckman['middlename'])
        self.failUnless(author2['firstname'] == heckman['firstname'])
        self.failUnless(author2['lastname'] == heckman['lastname'])

    def testBibtexInbookReferenceParsing(self):
        source = open(setup.BIBTEX_TEST_INBOOKREFERENCES, 'r').read()
        ref = {
            'booktitle': 'In einem fiktiven Buch vor unserer Zeit',
            'title': 'Die Tage der Ankunft',
            'chapter': 'Die Tage der Ankunft',
            'publication_url': 'http://www.sunweavers.net/',
        }

        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)

        for key in ref.keys():
            self.failUnless( result.has_key(key) and (ref[key] == result[key]) )

    def testAnnoteParsing(self):
        source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        results = self.parser.getEntries(source)
        self.failUnless(results[-1]['annote'] == 'I really like it.')

    def testBibtexTypeFieldParsing(self):
        source = open(setup.BIBTEX_TEST_TYPEFIELD, 'r').read()
        ref = {
            'publication_type': 'Doktorarbeit',
            'title': 'Mein Herr Doktor',
            'school': 'CAU Kiel',
            'institution': 'Ökologie-Zentrum',
        }

        source = self.parser.checkEncoding(source)
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)

        for key in ref.keys():
            self.failUnless( result.has_key(key) and (ref[key] == result[key]) )

    def testBibtexTypeLastFieldTrailingKomma(self):
        source = open(setup.BIBTEX_TEST_LASTFIELDKOMMA, 'r').read()
        results = self.parser.getEntries(source)

        # the last field in a bibtex entry always had a trailing ","
        self.failUnless( len(results) == 2  )
        self.failUnless( results[0]['institution'] == results[1]['institution']  )
        self.failUnless( results[0]['publication_type'] == results[1]['publication_type']  )
        self.failUnless( results[0]['publication_type'] == 'Doktorarbeit,,,' )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibtexParsing))
    return suite

if __name__ == '__main__':
    framework()

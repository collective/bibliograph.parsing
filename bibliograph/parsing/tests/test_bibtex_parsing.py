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
            self.failUnless( result.has_key(key) and (ref[key] == result[key]),key )

    def testAnnoteParsing(self):
        source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        results = self.parser.getEntries(source)
        self.failUnless(results[-1]['annote'] == 'I really like it.')

    def testIdentifierParsing(self):
        source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        results = self.parser.getEntries(source)
        result = results[2]
        self.assertEqual(result['identifiers'], [{'label' : 'ISBN', 'value' : '3874402436'},
                                                 {'label' : 'DOI', 'value' : '1-23-345'}])

    def testBibtexTypeFieldParsing(self):
        source = open(setup.BIBTEX_TEST_TYPEFIELD, 'r').read()
        ref = {
            'publication_type': 'Doktorarbeit',
            'title': 'Mein Herr Doktor',
            'school': 'CAU Kiel',
            'institution': 'Ã–kologie-Zentrum',
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

class TestBibtexParsing2(unittest.TestCase):
    """ more tests """

    def setUp(self):
        self.parser = BibtexParser()

    def testBibtexWithCustomFieldnames(self):
        source = open(setup.BIBTEX_TEST_BIB2, 'r').read()
        results = self.parser.getEntries(source)
        r1 = results[0]
        self.assertEqual(r1['month'], 'Mar')
        self.assertEqual(r1['doi'], '10.1002/(ISSN)1097-0231')
        self.assertEqual(r1['date-added'], '2008-08-06 17:48:48 +0200')
        self.assertEqual(r1['rating'], '0')
        self.assertEqual(r1['keywords'], ['biology', 'chemistry'])
        r2 = results[1]
        self.assertEqual(r2['keywords'], ['something strange'])

    def testBibtexEncodedChars(self):
        source = open(setup.BIBTEX_TEST_BIB3, 'r').read()
        results = self.parser.getEntries(source)
        self.assertEqual(len(results), 2)
        r = results[0]
        self.assertEqual(r['title'], unicode('Der Fürst', 'iso-8859-15').encode('utf-8'))
        self.assertEqual(r['publisher'], unicode('Alfred Körner Verlag', 'iso-8859-15').encode('utf-8'))
        r = results[1]
        self.assertEqual(r['address'], unicode('Göttingen', 'iso-8859-15').encode('utf-8'))
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibtexParsing))
    suite.addTest(makeSuite(TestBibtexParsing2))
    return suite

if __name__ == '__main__':
    framework()

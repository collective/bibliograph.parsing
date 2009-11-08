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
from types import UnicodeType
import codecs
import unittest

from bibliograph.core.interfaces import IAuthor
from bibliograph.core.interfaces import IIdentifier
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IArticleReference
from bibliograph.core.interfaces import IInbookReference
from bibliograph.core.interfaces import IIncollectionReference

from bibliograph.parsing.parsers.bibtex import BibtexParser
from bibliograph.parsing.tests import setup
from bibliograph.parsing.tests.base import BaseParserTestCase


class TestBibtexParsing(BaseParserTestCase):
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
            source = self.readFile(source_file)
            self.failUnless(self.parser.checkFormat(source),
                            'BibTeX parser failed to detect BibTeX format in file %s' % source_file)
        # check negative detection (check properly rejects non-bibtex format files)
        source = self.readFile(setup.MEDLINE_TEST_MED)
        self.failIf(self.parser.checkFormat(source),
                    'BibTeX parser incorrectly detected BibTeX format in file %s' % setup.MEDLINE_TEST_MED)

    def testBibtexUnicodeSupport(self):
        source = self.readFile(setup.BIBTEX_TEST_UNICODE)
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)
        self.failUnless(IArticleReference.providedBy(result))
        # Attributes should be stored as unicode
        self.failUnless(isinstance(result.title, UnicodeType))
        self.failUnless(isinstance(result.authors[0].lastname, UnicodeType))

    def testBibtexAuthorParsing(self):
        source = self.readFile(setup.BIBTEX_TEST_MULTI_AUTHORS)
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)
        self.failUnless(IBibliographicReference.providedBy(result))
        heckman =  {'middlename': 'J.',
                    'firstname' : 'James',
                    'lastname'  : 'Heckman'}
        carneiro = {'middlename': '',
                    'firstname' : 'Pedro',
                    'lastname'  : 'Carneiro'}
        self.failUnless( len(result.authors) == 2 )
        author1 = result.authors[0]
        self.failUnless(IAuthor.providedBy(author1))
        self.failUnless(author1.middlename == carneiro['middlename'])
        self.failUnless(author1.firstname == carneiro['firstname'])
        self.failUnless(author1.lastname == carneiro['lastname'])
        author2 = result.authors[1]
        self.failUnless(IAuthor.providedBy(author2))
        self.failUnless(author2.middlename == heckman['middlename'])
        self.failUnless(author2.firstname == heckman['firstname'])
        self.failUnless(author2.lastname == heckman['lastname'])

    def testBibtexInbookReferenceParsing(self):
        source = self.readFile(setup.BIBTEX_TEST_INBOOKREFERENCES)
        ref = {
            'volumetitle': 'In einem fiktiven Buch vor unserer Zeit',
            'title': 'Die Tage der Ankunft',
            #'chapter': 'Die Tage der Ankunft',
            #'publication_url': 'http://www.sunweavers.net/',
        }
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)
        self.failUnless(IInbookReference.providedBy(result))
        for key in ref.keys():
            value = getattr(result, key, None)
            self.failUnless( ref[key] == value, (key, ref[key], value) )

    def testBibtexIncollectionChapterHandling(self):
        source = self.readFile(setup.BIBTEX_TEST_INCOLLECTIONCHAPTER)
        ref = {
            'volumetitle': u'Order and Conflict in Contemporary Capitalism',
            'title': u'Market-Independent Income Distribution: Efficiency and Legitimacy',
            'chapter': u'9',
        }
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)
        self.failUnless(IIncollectionReference.providedBy(result))
        for key in ref.keys():
            value = getattr(result, key, None)
            self.failUnless( ref[key] == value, (key, ref[key], value) )

    def testAnnoteParsing(self):
        source = self.readFile(setup.BIBTEX_TEST_BIB)
        results = self.parser.getEntries(source)
        self.failUnless(results[-1].annote == 'I really like it.')

    def testBibtexTypeFieldParsing(self):
        # XXX It's not clear to me why we have this 'publication_type' field...
        source = self.readFile(setup.BIBTEX_TEST_TYPEFIELD)
        ref = {
            #'publication_type': u'Doktorarbeit',
            'title': u'Mein Herr Doktor',
            'school': u'CAU Kiel',
            'institution': u'Ökologie-Zentrum',
        }
        source = self.parser.checkEncoding(source)
        source = self.parser.preprocess(source)
        result = self.parser.parseEntry(source)
        self.failUnless(IBibliographicReference.providedBy(result))
        for key in ref.keys():
            value = getattr(result, key, None)
            self.failUnless( ref[key] == value, value )

    def testBibtexTypeLastFieldTrailingKomma(self):
        source = self.readFile(setup.BIBTEX_TEST_LASTFIELDKOMMA)
        results = self.parser.getEntries(source)
        # the last field in a bibtex entry always had a trailing ","
        self.failUnless( len(results) == 2  )
        self.failUnless( results[0].institution == results[1].institution )
        #self.failUnless( results[0].publication_type == results[1].publication_type )
        #self.failUnless( results[0].publication_type == 'Doktorarbeit' )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibtexParsing))
    return suite

if __name__ == '__main__':
    framework()

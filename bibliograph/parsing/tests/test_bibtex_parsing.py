# -*- encoding: utf-8 -*-
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

__revision__ = '$Id:  $'


import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFBibliographyAT.tests import setup
from ZODB.PersistentList import PersistentList
from Globals import PersistentMapping

#ZopeTestCase.installProduct('DeadlockDebugger')
#import Products.DeadlockDebugger

class TestBibtexParsing(PloneTestCase.PloneTestCase):
    """
    """

    def afterSetUp(self):
        self._refreshSkinData()

    def testBibtexAuthorParsing(self):
        bibtool = self.portal.portal_bibliography
        p = bibtool.getParser('bibtex')
        source = open(setup.BIBTEX_TEST_MULTI_AUTHORS, 'r').read()
        source = p.preprocess(source)
        result = p.parseEntry(source)
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
        bibtool = self.portal.portal_bibliography
        p = bibtool.getParser('bibtex')
        source = open(setup.BIBTEX_TEST_INBOOKREFERENCES, 'r').read()
        ref = {
            'booktitle': 'In einem fiktiven Buch vor unserer Zeit',
            'title': 'Die Tage der Ankunft',
            'chapter': 'Die Tage der Ankunft',
            'publication_url': 'http://www.sunweavers.net/',
        }

        source = p.preprocess(source)
        result = p.parseEntry(source)

        for key in ref.keys():
            self.failUnless( result.has_key(key) and (ref[key] == result[key]) )

    def testAnnoteParsing(self):
        bibtool = self.portal.portal_bibliography
        p = bibtool.getParser('bibtex')
        source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        results = p.getEntries(source)
        self.failUnless(results[-1]['annote'] == 'I really like it.')

    def testBibtexTypeFieldParsing(self):
        bibtool = self.portal.portal_bibliography
        p = bibtool.getParser('bibtex')
        source = open(setup.BIBTEX_TEST_TYPEFIELD, 'r').read()
        ref = {
            'publication_type': 'Doktorarbeit',
            'title': 'Mein Herr Doktor',
            'school': 'CAU Kiel',
            'institution': 'Ökologie-Zentrum',
        }

        source = bibtool.checkEncoding(source)
        source = p.preprocess(source)
        result = p.parseEntry(source)

        for key in ref.keys():
            self.failUnless( result.has_key(key) and (ref[key] == result[key]) )

    def testBibtexTypeLastFieldTrailingKomma(self):
        bibtool = self.portal.portal_bibliography
        p = bibtool.getParser('bibtex')
        source = open(setup.BIBTEX_TEST_LASTFIELDKOMMA, 'r').read()

        source = bibtool.checkEncoding(source)
        source = p.preprocess(source)
        results = p.getEntries(source)

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

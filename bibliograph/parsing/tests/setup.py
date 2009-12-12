# This is so we can find our sample test files
from bibliograph.parsing.tests import GLOBALS
from Globals import package_home
PACKAGE_HOME = package_home(GLOBALS)

from os.path import join
MEDLINE_TEST_MED = join(PACKAGE_HOME, 'samples', 'medline_test.med')
MEDLINE_TEST_BIB = join(PACKAGE_HOME, 'samples', 'medline_test.bib')
MEDLINE_TEST_XML = join(PACKAGE_HOME, 'samples', 'medline_test.xml')
BIBTEX_TEST_BIB = join(PACKAGE_HOME, 'samples', 'bibtex_test.bib')
BIBTEX_TEST_BIB2 = join(PACKAGE_HOME, 'samples', 'bibtex_test2.bib')
BIBTEX_TEST_BIB3 = join(PACKAGE_HOME, 'samples', 'bibtex_test3.bib')
IDCOOKING_TEST_BIB = join(PACKAGE_HOME, 'samples', 'idcooking_test.bib')
PDFFOLDER_TEST_BIB = join(PACKAGE_HOME, 'samples', 'pdffolder_test.bib')
CMFBAT_TEST_PDF_1 = join(PACKAGE_HOME, 'samples', 'cmfbat-pdffile1.pdf')
CMFBAT_TEST_PDF_2 = join(PACKAGE_HOME, 'samples', 'cmfbat-pdffile2.pdf')
CMFBAT_TEST_PDF_3 = join(PACKAGE_HOME, 'samples', 'cmfbat-pdffile3.pdf')
BIBTEX_TEST_BIB_DUP = join(PACKAGE_HOME, 'samples', 
                           'bibtex_test_duplicates.bib')
BIBTEX_TEST_MULTI_AUTHORS = join(PACKAGE_HOME, 'samples',
                                 'bibtex_test_multiauthors.bib')
BIBTEX_TEST_INBOOKREFERENCES = join(PACKAGE_HOME, 'samples',
                                 'bibtex_test_inbookreferences.bib')
BIBTEX_TEST_LASTFIELDKOMMA = join(PACKAGE_HOME, 'samples',
                                 'bibtex_test_lastfieldkomma.bib')
BIBTEX_TEST_TYPEFIELD = join(PACKAGE_HOME, 'samples',
                                 'bibtex_test_typefield.bib')
BIBTEX_TEST_CITE_KEY = join(PACKAGE_HOME, 'samples',
                            'bibtex_test_cite_key.bib')
RIS_SOURCE = join(PACKAGE_HOME, 'samples', 'ris_test.ris')
ENDNOTE_TEST_SOURCE = join(PACKAGE_HOME, 'samples', 'endnote.end')

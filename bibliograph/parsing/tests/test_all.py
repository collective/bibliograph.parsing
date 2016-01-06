import pdb; pdb.set_trace()

from unittest import TestSuite

from test_base import test_suite as base_suite
from test_bibtex_parsing import test_suite as bibtex_suite
from test_endnote_parser import test_suite as endnote_suite
from test_medline_parser import test_suite as medline_suite
from test_ris_parser import test_suite as ris_suite
from test_xml_parser import test_suite as xml_suite


def test_suite():
    suite = TestSuite()
    for suite_fn in [
        base_suite,
        bibtex_suite,
        endnote_suite,
        medline_suite,
        ris_suite,
        xml_suite,
    ]:
        suite.addTest(suite_fn())
    return suite

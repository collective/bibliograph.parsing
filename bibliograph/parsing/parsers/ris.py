############################################################################
#                                                                          #
#             copyright (c) 2004, 2006 ITB, Humboldt-University Berlin     #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""RISParser class (Research Information Systems/Reference Manager)"""

# Python stuff
import os

# Zope stuff
from zope.component import getUtility

from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from bibliograph.rendering.interfaces import IBibTransformUtility

from Products.CMFCore.utils import getToolByName
from bibliograph.parsing.parsers.base \
     import IBibliographyParser, BibliographyParser
from bibliograph.parsing.parsers.base import isTransformable

#try:
#    import _bibtex
#    from bibliograph.parsing.parsers.pyblbibtex \
#         import PyBlBibtexParser as BaseParser
from bibliograph.parsing.parsers.bibtex \
     import BibtexParser as BaseParser


month_mapper = {'jan' : '01',
                'feb' : '02',
                'mar' : '03',
                'apr' : '04',
                'may' : '05',
                'jun' : '06',
                'jul' : '07',
                'aug' : '08',
                'sep' : '09',
                'oct' : '10',
                'nov' : '11',
                'dec' : '12',
                'january'  : '01',
                'february' : '02',
                'march'    : '03',
                'april'    : '04',
                'may'      : '05',
                'june'     : '06',
                'july'     : '07',
                'august'   : '08',
                'september': '09',
                'october'  : '10',
                'november' : '11',
                'december' : '12',
               }

def fixMonth(s):
    s_lower = s.lower()
    if month_mapper.has_key(s_lower):
        return month_mapper[s_lower]
    return s


class RISParser(BaseParser):
    """
    A specific parser to process input in RIS format (Research Information Systems/Reference Manager).
    """

    __implements__ = (IBibliographyParser ,)

    meta_type = "RIS Parser"

    format = {'name':'RIS',
              'extension':'ris'}

    def __init__(self,
                 id = 'ris',
                 title = "RIS format parser"
                 ):
        """
        initializes including the regular expression patterns
        """
        BaseParser.__init__(self, id=id, title=title)

    # Here we need to provide 'checkFormat' and 'preprocess'

    def isAvailable(self):
        """ test if transforming from RIS format to BibTex is possible...
        """
        return isTransformable('ris', 'bib')

    def checkFormat(self, source):
        """
        is this RIS format?
        (Research Information Systems/Reference Manager)
        """
        teststring = source[:200].lower()
        ai = teststring.find('AU ')
        ei = teststring.find('TI ')
        di = teststring.find('PY ')
        if ai + ei + di > -2:
            return 1
        else:
            return 0

    def preprocess(self, source):
        """
        convert RIS to BibTeX
        """
        tool = getUtility(IBibTransformUtility, name=u"external")
        return tool.transform(source, 'ris', 'bib')

    def parseEntry(self, entry):
        """See IBibliographyParser.
        """
        rd = super(RISParser, self).parseEntry(entry) # rd for 'result_dict'
        if not rd.has_key('number') and rd.has_key('issue'):
            rd['number'] = rd['issue'].replace(' ', '')
        rd['publication_month'] = fixMonth(rd['publication_month'])
        return rd

    # all the rest we inherit from our parent BibTeX(!) parser

InitializeClass(RISParser)


def manage_addRISParser(self, REQUEST=None):
    """ """
    try:
        self._setObject('ris', RISParser())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)

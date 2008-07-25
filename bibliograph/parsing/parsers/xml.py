############################################################################
#                                                                          #
#             copyright (c) 2004 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""XMLParser (MODS) class"""

# Python stuff
import re, os

# Zope stuff
from zope.component import getUtility

# Bibliography stuff
from bibliograph.rendering.interfaces import IBibTransformUtility
from bibliograph.parsing.parsers.base import isTransformable
from bibliograph.parsing.parsers.bibtex import BibtexParser as BaseParser


class XMLParser(BaseParser):
    """
    A specific parser to process input in XML(MODS)-format. The XML intermediate format is conform to the
    Library of Congress's Metadata Object Description Schema (MODS). This is a very flexible standard that
    should prove quite useful as the number of tools that directly interact with it increase.
    """

    meta_type = "XML (MODS) Parser"

    format = {'name':'XML (MODS)',
              'extension':'xml'}

    def __init__(self,
                 id = 'xml_mods',
                 title = "XML(MODS) parser"
                 ):
        """
        initializes including the regular expression patterns
        """
        BaseParser.__init__(self, id=id, title=title)

    # Here we need to provide 'isAvailable', 'checkFormat' and 'preprocess'

    def isAvailable(self):
        """ test if transforming from XML to BibTex is possible...
        """
        return isTransformable('xml', 'bib')

    def checkFormat(self, source):
        """ is this my format?
        """
        teststring = source[:200].lower()
        ai = teststring.find('www.loc.gov/mods')
        ei = teststring.find('modsCollection')
        if ai + ei > -2:
            return 1
        else:
            return 0

    def preprocess(self, source):
        """
        convert XML to BibTeX
        """
        tool = getUtility(IBibTransformUtility, name=u"external")
        return tool.transform(source, 'xml', 'bib')

    # all the rest we inherit from our parent BibTeX(!) parser

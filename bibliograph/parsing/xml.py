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

from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from bibliograph.rendering.interfaces import IBibTransformUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.tool.parsers.base \
     import IBibliographyParser, BibliographyParser
from Products.CMFBibliographyAT.tool.parsers.base import isTransformable

try:
    import _bibtex
    from Products.CMFBibliographyAT.tool.parsers.pyblbibtex \
         import PyBlBibtexParser as BaseParser
except ImportError:
    from Products.CMFBibliographyAT.tool.parsers.bibtex \
         import BibtexParser as BaseParser


class XMLParser(BaseParser):
    """
    A specific parser to process input in XML(MODS)-format. The XML intermediate format is conform to the
    Library of Congress's Metadata Object Description Schema (MODS). This is a very flexible standard that
    should prove quite useful as the number of tools that directly interact with it increase.
    """

    __implements__ = (IBibliographyParser,)

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
        """
        is this my format?
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

InitializeClass(XMLParser)


def manage_addXMLParser(self, REQUEST=None):
    """ """
    try:
        self._setObject('xml_mods', XMLParser())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)

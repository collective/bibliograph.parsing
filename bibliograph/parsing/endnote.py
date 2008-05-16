############################################################################
#                                                                          #
#             copyright (c) 2004, 2006 ITB, Humboldt-University Berlin     #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""EndNoteParser class"""

# Python stuff
import os

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


class EndNoteParser(BaseParser):
    """
    A specific parser to process input in EndNote's text format.
    """

    __implements__ = (IBibliographyParser ,)

    meta_type = "EndNote Parser"

    format = {'name':'EndNote',
              'extension':'end'}

    def __init__(self,
                 id = 'endnote',
                 title = "EndNote's text format parser"
                 ):
        """
        initializes including the regular expression patterns
        """
        BaseParser.__init__(self, id=id, title=title)

    # Here we need to provide 'checkFormat' and 'preprocess'

    def isAvailable(self):
        """ test if transforming from Endnote to BibTex is possible...
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        return isTransformable('end', 'bib')

    def checkFormat(self, source):
        """
        is this my format?
        """
        teststring = source[:200].lower()
        ai = teststring.find('%T')
        ei = teststring.find('%A')
        di = teststring.find('%D')
        if ai + ei + di > -2:
            return 1
        else:
            return 0

    def preprocess(self, source):
        """
        convert EndNote to BibTeX
        """
        tool = getUtility(IBibTransformUtility, name=u"external")
        return tool.transform(source, 'end', 'bib')

    # all the rest we inherit from our parent BibTeX(!) parser

InitializeClass(EndNoteParser)


def manage_addEndNoteParser(self, REQUEST=None):
    """ """
    try:
        self._setObject('endnote', EndNoteParser())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)

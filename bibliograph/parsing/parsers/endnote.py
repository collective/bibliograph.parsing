############################################################################
#                                                                          #
#             copyright (c) 2004, 2006 ITB, Humboldt-University Berlin     #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""EndNoteParser class"""

# Zope stuff
from zope.component import getUtility 
from zope.interface import implements

# Bibliography stuff
from bibliograph.rendering.interfaces import IBibTransformUtility

from bibliograph.parsing.parsers.base import IBibliographyParser
from bibliograph.parsing.parsers.base import isTransformable

try:
    import _bibtex
    from bibliograph.parsing.parsers.pyblbibtex \
         import PyBlBibtexParser as BaseParser
except ImportError:
    from bibliograph.parsing.parsers.bibtex \
         import BibtexParser as BaseParser


class EndNoteParser(BaseParser):
    """
    A specific parser to process input in EndNote's text format.
    """

    implements(IBibliographyParser)
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

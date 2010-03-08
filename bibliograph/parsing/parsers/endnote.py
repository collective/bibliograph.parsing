############################################################################
#                                                                          #
#             copyright (c) 2004, 2006 ITB, Humboldt-University Berlin     #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""EndNoteParser class"""
# Python stuff
import re

# Zope stuff
from zope.component import getUtility 
from zope.interface import implements

# Bibliography stuff
from bibliograph.rendering.interfaces import IBibTransformUtility
from bibliograph.parsing.parsers.base import isTransformable
from bibliograph.parsing.parsers.bibtex import BibtexParser as BaseParser


class EndNoteParser(BaseParser):
    """
    A specific parser to process input in EndNote's text format.
    """

    format = {'name':'EndNote',
              'extension':'enw'}

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
        does the source look to be in endnote format?
        """
        # Ultimately end2xml is used
        # http://www.scripps.edu/~cdputnam/software/bibutils/bibutils2.html#end2xml

        pattern = re.compile('^%[0-9|A-Z] ', re.M)
        all_tags = re.findall(pattern, source)
        # Should always start w/ '%0' and have at least one author '%A',
        # a year (date) '%D' and a title '%T'
        required = ('%A ', '%D ', '%T ')
        if len(all_tags) and all_tags[0] == '%0 ' and \
                reduce(lambda i, j: i and j, [r in all_tags for r in required]):
            return 1
        else:
            return 0

    def preprocess(self, source):
        """
        prep the source and convert EndNote to BibTeX
        """
        # Remove carriage returns - end2xml chokes on them
        source = source.replace('\r', '')

        tool = getUtility(IBibTransformUtility, name=u"external")
        return tool.transform(source, 'end', 'bib')

    # all the rest we inherit from our parent BibTeX(!) parser

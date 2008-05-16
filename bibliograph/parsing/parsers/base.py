############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""BibliographyParser main class"""

# Python stuff
import re

# Zope stuff
from zope.interface import implements
from Interface import Interface
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Acquisition import Implicit
import Products

from bibliograph.rendering.utility import _getKey
from bibliograph.rendering.utility import commands

from Products.CMFBibliographyAT.interface import \
     IBibliographyParser as z3IBibliographyParser
from Products.CMFBibliographyAT.interface import IBibliographyParserFolder


class IBibliographyParser(Interface):
    """
    Interface for the input parsers of the bibliography tool.
    """
    def isAvailable():
        """
        are all pre-requisites for this parser fullfilled?
        """

    def isEnabled():
        """
        is this parser enabled by the portal manager (default: yes)?
        """

    def getFormatName():
        """
        returns the name of the format
        """

    def getFormatExtension():
        """
        returns the filename extension of the format
        """

    def getDelimiter():
        """
        returns the delimiter used to split a list of entries into pieces
        """

    def getPattern():
        """
        returns the pattern used to parse a single entry
        """

    def setDelimiter(delimiter="\n\n", flags=None):
        """
        sets the delimiter used to split a list of entries into pieces
        the 'delimiter' argument and the flags are passed to 're.compile'
        """

    def setPattern(pattern="\n", flags=None):
        """
        sets the pattern used to parse a single entry
        the 'pattern' argument is passed to 're.compile')
        """

    def checkFormat(source):
        """
        checks whether source has the right format
        returns true (1) if so and false (0) otherwise
        """

    def getEntries(source):
        """
        splits a (text) file with several entries
        parses the entries
        returns a list of the parsed entries
        """

    def splitSource(source):
        """
        splits a (text) file with several entries
        returns a list of those entries
        """

    def parseEntry(entry):
        """
        parses a single entry

        returns a dictionary to be passed to
        BibliographyEntry's edit method
        """


class BibliographyParser(SimpleItem, PropertyManager):
    """
    Base class for the input parser of the bibliography tool.
    """
    __implements__ = (IBibliographyParser,)
    implements(z3IBibliographyParser)

    meta_type = 'Bibliography Parser'
    parser_enabled = True
    format = {'name':'name of the format',
              'extension':'typical filename extension'
              }

    manage_options = (
        PropertyManager.manage_options +
        SimpleItem.manage_options
    )
    _properties = PropertyManager._properties + (
        {'id':'parser_enabled',
         'type':'boolean',
         'mode':'w',
         },
    )

    security = ClassSecurityInfo()

    delimiter = "\n\n"       # used to split a text into a list of entries
    pattern = r'(^.{0,4}- )' # the Medline pattern as default

    def __init__(self, id, title=''):
        """
        minimal initialization
        """
        self.id = id
        self.title = title
        self.format = format

    def isAvailable(self):
        """ by default parser is available, override in specific parser's code
            if there are some hurdles to take before parsing is possible
        """
        return True

    def isEnabled(self):
        """ if parser is enabled or not can be configured in the PropertyManager
        """
        return self.parser_enabled

    def Description(self):
        """
        a short text that explains the target format of the renderer
        """
        domain='cmfbibliographyat'
        msgid='help_parser_%s' % self.getId()
        return self.translate(domain=domain, msgid=msgid, default='%s' % self.__doc__)

    def getFormatName(self):
        """ returns the name of the format """
        return self.format.get('name', 'No name specified')

    def getFormatExtension(self):
        """ returns the filename extension of the format """
        return self.format.get('extension', 'no extension specified')

    def getDelimiter(self):
        """
        returns the delimiter used to split a list of entries into pieces
        """
        return self.delimiter

    def getPattern(self):
        """
        returns the pattern used to parse a single entry
        """
        return self.pattern

    def setDelimiter(self, delimiter="\n\n", flags=None):
        """
        sets the delimiter used to split a list of entries into pieces
        the 'delimiter' argument and the flags are passed to 're.compile'
        """
        if flags:
            self.delimiter = re.compile(delimiter, flags)
        else:
            self.delimiter = re.compile(delimiter)
        return None

    def setPattern(self, pattern="\n", flags=None):
        """
        sets the pattern used to parse a single entry
        the 'pattern' argument is passed to 're.compile')
        """
        if flags:
            self.pattern = re.compile(pattern, flags)
        else:
            self.pattern = re.compile(pattern)
        return None

    def checkFormat(source):
        """
        checks whether source has the right format
        returns true (1) if so and false (0) otherwise
        """
        pass # needs to be provided by the individual parsers

    def splitSourceFile(self, source):
        """
        splits a (text) file with several entries
        returns a list of those entries
        """
        if hasattr(self, 'preprocess'):
            source = self.preprocess(source)
        return self.delimiter.split(source)

    def parseEntry(self, entry):
        """
        parses a single entry

        returns a dictionary to be passed to
        BibliographyEntry's edit method
        """
        pass  # needs to be overwriten by the individual parser

    def getEntries(self, source):
        """
        splits a (text) file with several entries
        parses the entries
        returns a list of the parsed entries
        """
        return [self.parseEntry(entry) \
                for entry in self.splitSourceFile(source)]


InitializeClass(BibliographyParser)

class ParserFolder(Folder):
    """
    A folder that only offers to add objects that implement the
    IBibliographyParser interface.
    """
    implements(IBibliographyParserFolder)
    meta_type = 'Parser Folder'

    id = 'Parsers'
    title = "BibliographyTool's parser folder"

    # we don't want 'View'
    manage_options = ( Folder.manage_options[0], ) \
                     + Folder.manage_options[2:]
    index_html = None

    def __init__(self, id, title=''):
        """
        minimal initialization
        """
        self.id = id
        # self.title = title

    def all_meta_types(self):
        product_infos = Products.meta_types
        possibles = []
        for p in product_infos:
            try:
                if IBibliographyParser in p.get('interfaces', []):
                    possibles.append(p)
            except TypeError:
                pass
        definites = map(lambda x: x.meta_type, self.objectValues())
        return filter(lambda x,y=definites: x['name'] not in y, possibles)

InitializeClass(ParserFolder)


class EntryParseError(Implicit):
    """Parsers can return instances of this class when the parsing
    of an entry fails for whatever reason.
    The description is then taken and added to the import_report.
    """

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, description):
        self.description = description.replace('\n', '\\n')

    security.declarePublic('get')
    def get(self, attr_name):
        # XXX Hack! import.cpy does::
        #    if entry.get('title'):
        #        ...
        # So we need to mimic that here
        if attr_name == 'description':
            return self.description
        else:
            return 'EntryParseError'

def isTransformable(source_format, target_format):
    """
    test if a transform from source_format to target_format.
    would be feasible
    """
    key = _getKey(source_format, target_format)
    command = commands.get(key, None)
    if command is None:
        return False
    commandlist = [ c.strip() for c in command.split('|') ]

    # open each command once
    transformable = True
    for c in commandlist:

        pass

    return transformable

InitializeClass(EntryParseError)

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

from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.core.bibutils import _getCommand


class BibliographyParser(object):
    """
    Base class for the input parser of the bibliography tool.
    """
    implements(IBibliographyParser)

    parser_enabled = True
    format = {'name':'name of the format',
              'extension':'typical filename extension'
              }

    delimiter = "\n\n"       # used to split a text into a list of entries
    pattern = r'(^.{0,4}- )' # the Medline pattern as default

    def __init__(self):
        """
        minimal initialization
        """
        self.format = BibliographyParser.format

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
        a short text that explains the target format of the parser
        """
        # TODO i18n this method, port to bibliograph.parsing domain
        # domain='cmfbibliographyat'
        # msgid='help_parser_%s' % self.getId()
        # return self.translate(domain=domain, msgid=msgid, default='%s' % self.__doc__)
        return self.__doc__

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

    def checkFormat(self, source):
        """
        checks whether source has the right format
        returns true (1) if so and false (0) otherwise
        """
        pass # needs to be provided by the individual parsers

    def splitSource(self, source):
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
        source = self.checkEncoding(source)
        return [self.parseEntry(entry) \
                for entry in self.splitSource(source)]

    def checkEncoding(self, source):
        """
        Make sure we have utf encoded text
        """
        try:
            source = unicode(source, 'utf-8')
        except UnicodeDecodeError:
            source = unicode(source, 'iso-8859-15')
        return source.encode('utf-8')


class EntryParseError(object):
    """Parsers can return instances of this class when the parsing
    of an entry fails for whatever reason.
    The description is then taken and added to the import_report.
    """

    def __init__(self, description):
        self.description = description.replace('\n', '\\n')

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
    try:
        _getCommand(source_format, target_format)
    except (ValueError, LookupError):
        return False

    return True

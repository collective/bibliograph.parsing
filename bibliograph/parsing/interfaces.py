from zope.interface import Interface


class IBibliographyParser(Interface):
    """ Interface for bibliographic input parsers
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

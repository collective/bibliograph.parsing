from zope.interface import Interface


class IParserImplementationDetail(Interface):
    """This constitutes an implementation detail which is useful for parser
    implementers but not for users of the parsers.
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

    def splitSource(source):
        """
        splits a (text) file with several entries
        returns a list of those entries
        """

    def getDelimiter():
        """
        returns the delimiter used to split a list of entries into pieces
        """

    def parseEntry(entry,
                   author=None,
                   identifier=None,
                   article=None,
                   book=None,
                   booklet=None,
                   conference=None,
                   inbook=None,
                   incollection=None,
                   inproceedings=None,
                   manual=None,
                   misc=None,
                   masterthesis=None,
                   phdthesis=None,
                   preprint=None,
                   proceedings=None,
                   techreport=None,
                   unpublished=None,
                   webpublished=None
                   ):
        """
        parses a single entry

        returns a dictionary to be passed to
        BibliographyEntry's edit method
        """


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

    def getEntries(source, **kw):
        """
        Splits a (text) file with several entries and parses the entries.
        Returns a list of the parsed entries. Keyword arguments beyond `source'
        set the classes/factories that are used for the parsed entries.
        """


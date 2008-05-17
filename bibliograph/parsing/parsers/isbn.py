############################################################################
#                                                                          #
#             copyright (c) 2004 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""ISBNParser (via Amazon) class"""

# Python stuff
import re, string
from types import StringTypes

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from Products.CMFCore.utils import getToolByName
from bibliograph.parsing.parsers.base \
     import IBibliographyParser, BibliographyParser
from bibliograph.parsing.parsers.base \
     import EntryParseError


class ISBNParser(BibliographyParser):
    """
    A specific parser to process a list of ISBN numbers. Information will be retrieved from Amazon Webservices.
    """

    __implements__ = (IBibliographyParser ,)

    meta_type = "ISBN Parser"

    format = {'name':'ISBN',
              'extension':'isbn'}

    def __init__(self,
                 id = 'isbn',
                 title = "ISBN parser via Amazon",
                 delimiter = '\n', # split on newlines
                 pattern = r'(^.{0,4}- )', # obsolete
                 flag = re.M):
        """
        initializes including the regular expression patterns
        """
        self.id = id
        self.title = title
        self.setDelimiter(delimiter)
        self.setPattern(pattern, flag)


    # Here we need to provide 'isAvailable', 'checkFormat' and 'parseEntry'

    def isAvailable(self):
        # in order not to get confused with ATAmazon, we quickly query the
        # quickinstaller for the product name
        qi = getToolByName(self, 'portal_quickinstaller')
        amazontool_installed = qi.isProductInstalled('AmazonTool')
        # and, of course, we need a valid license key in the AmazonTool setup...
        amazon_tool = getToolByName(self, 'amazon_tool', False)
        return amazontool_installed and amazon_tool.hasValidLicenseKey()

    def checkFormat(self, source):
        """
        is this my format?
        """
        # are these ISBN numbers?
        # naive check: does the first line contain at least 8 digits
        ## rr: can definitively be improved
        first_line = source.split('\n')[0]
        count = 0
        for c in first_line:
            if c.isdigit(): count += 1
        if count > 7:
            return 1
        else:
            return 0

    def parseEntry(self, entry):
        """
        parses a single entry

        returns a dictionary to be passed to
        BibliographyEntry's edit method
        """
        result = {}
        entry = self._normalizeEntry(entry)
        if isinstance(entry, EntryParseError):
            return entry
        amazon_tool = getToolByName(self, 'amazon_tool')
        try:
            a_result = amazon_tool.searchByASIN(asin=entry)[0]
        except Exception, detail:
            return EntryParseError(detail.__str__())
        result['reference_type'] = 'BookReference'
        result['authors'] = self._makeAuthorList(a_result.Authors)
        result['title'] = a_result.ProductName
        result['publisher'] = a_result.Manufacturer
        result['isbn'] = entry
        # not sure whether the following is correct
        pdate = a_result.ReleaseDate.split(', ')
        result['publication_year'] = pdate[1]
        result['publication_month'] = pdate[0].split(' ')[-1]
        return result

    def _makeAuthorList(self, a_list):
        authors = []
        if isinstance(a_list, StringTypes):
            a_list = [a_list]
        for each in a_list:
            author = {}
            l = each.split(' ')
            author['firstname'] = l[0]
            if len(l) == 3:
                author['middlename'] = l[1]
                author['lastname'] = l[2]
            else:
                author['middlename'] = ''
                author['lastname'] = l[1]
            authors.append(author)
        return authors

    def _normalizeEntry(self, entry):
        allowed = string.ascii_letters + string.digits
        result = []
        for c in entry:
            if c in allowed:
                result.append(c)
        if result:
            return ''.join(result)
        else:
            return EntryParseError('malformed ISBN number: %s' % entry)

InitializeClass(ISBNParser)


def manage_addISBNParser(self, REQUEST=None):
    """ """
    try:
        getattr(self, 'amazon_tool')
    except AttributeError:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='You need to install the AmazonTool before you can install this parser.',
            action='manage_main')
    try:
        self._setObject('isbn', ISBNParser())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')


    return self.manage_main(self, REQUEST)

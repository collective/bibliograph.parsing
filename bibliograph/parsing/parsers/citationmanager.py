############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""CitationManager parser class"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from bibliograph.parsing.parsers.base import BibliographyParser
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.base import EntryParseError

# Python standard library imports
import re
from cStringIO import StringIO
from types import StringType


# mapping from Citation Manager keys to CMBBib keys
key_mapping = {  'TI'   : 'title'
               , 'AB'   : 'abstract'
               #, 'GR' :
               #, 'FT' :
               #, 'AU' : Murphy, Kevin M.; Shleifer, Andrei; Vishny, Robert W.
               , 'SO' : 'journal'
               #, 'S2' :
               , 'VO' : 'volume'
               , 'NO' : 'number'
               #, 'SE' :
               #, 'DA' : May, 1991
               , 'PP' : 'pages'
               , 'EI' : 'publication_url'
               #, 'IN' : 00335533
               #, 'KW' :
               , 'PB' : 'publisher'
               #, 'LO' :
               #, 'LA' :
               #, 'CR' : Copyright 1991 The MIT Press
              }


class ParseException(Exception):
    pass


class CitationManagerParser(BibliographyParser):
    """
    A specific parser to process input in CitationManager format.
    """

    meta_type = "CitationManager Parser"

    format = {'name':'CitationManager',
              'extension':'txt'}

    def __init__(self,
                 id = 'citationmanager',
                 title = "CitationManager parser",
                 delimiter = '\n\n',
                 #pattern = r'(^.{0,4}- )',
                 flag = re.M):
        """
        initializes including the regular expression patterns
        """
        self.id = id
        self.title = title
        self.setDelimiter(delimiter)
        #self.setPattern(pattern, flag)


    # Here we need to provide 'checkFormat' and 'parseEntry'


    def preprocess(self, source):
        """ remove superfluous <CR>s
        """
        return source.replace('\r','')

    def checkFormat(self, source):
        """
        is this my format?
        """
        #raise Exception(type(source))
        #if source.find('      AU: ') > -1:
        #    return 1
        #else:
        #    return 0
        return True

    def parseEntry(self, entry):
        """
        parses a single entry

        returns a dictionary to be passed to
        BibliographyEntry's edit method
        """
        if isinstance(entry, StringType):
            entry = StringIO(entry)
        key = ''
        val = []
        record = {}
        first_line = True
        new_field = True
        for line in entry.readlines():
            if line[0] == '<' or line[0].strip() == '':
                # we ignore the number markers e.g. '<1>' and extra empty
                # lines
                continue
            find_delimiter = line.find(' : ')
            if find_delimiter != -1:
                new_field = True
            if new_field and not first_line:
                record[key] = ' '.join(val)
                val = []
            if new_field:
                key, value = line.split(' : ')
                val.append( value.strip() )
            else:
                val.append( line.strip() )
                #record[key] = '\n'.join(val)
            first_line = False
        result = {}
        if record['IT'] != 'FLA':
            # FLA seems to mean article.  We don't know how to deal with
            # anything else.
            entry.seek(0)
            raise EntryParseError(entry.read().replace('\n', '\\n'))
        result['reference_type'] = 'ArticleReference'
        self._parseAU(record['AU'], result)
        self._parseDate(record['DA'], result)
        for key in key_mapping.keys():
            if record.has_key(key):
                result[key_mapping[key]] = record[key]
        return result

    def _parseAU(self, s, result):
        # e.g. 'Murphy, Kevin M.; Shleifer, Andrei; Vishny, Robert W.'
        d = []
        l = s.split('; ')
        for person in l:
            p = {}
            p['lastname'], forenames = person.split(', ')
            forenames = forenames.split(' ')
            p['firstname'] = forenames[0]
            if len(forenames) > 1:
                p['middlename'] = ' '.join(forenames[1:])
            else:
                p['middlename'] = ''
            d.append(p)
        result['authors'] = d

    def _parseDate(self, s, result):
        # e.g. "Mar., 1967"
        month, year = s.split(', ')
        result['publication_year'] = year
        result['publication_month'] = month

############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""BIDSParser class"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from Products.CMFBibliographyAT.tool.parsers.base \
     import IBibliographyParser, BibliographyParser
from Products.CMFBibliographyAT.tool.parsers.base \
     import EntryParseError

# Python standard library imports
import re
from cStringIO import StringIO
from types import StringType


# mapping from IBSS keys to CMBBib keys
key_mapping = {  'TI'   : 'title'
               , 'AB'   : 'abstract'
              }

# keys that are (potentially) returned from _parseXX methods
parse_key_list = [  'publication_year'
                  , 'journal'
                  , 'publication_month'
                  , 'volume'
                  , 'number'
                  , 'pages'
                  , 'editor'
                  , 'chapter'
                  , 'authors'
                  , 'abstract'
                  , 'publisher'
                  , 'address'
                  , 'booktitle']


year_re = re.compile(', (\d\d\d\d)')
month_year_re = re.compile(', ([a-zA-Z\-]+) (\d\d\d\d),')
p_re = re.compile('(\d+)p\.')
p_re2 = re.compile('p\.(\d+)')
pp_re = re.compile('pp\.(\d+-\d+)')
vol_no_re = re.compile('Vol\.(\d+)\((\d+)\)')
vol_re = re.compile('Vol\.(\d+),')
no_re = re.compile('No.(\d+),')


class ParseException(Exception):
    pass


class IBSSParser(BibliographyParser):
    """
    A specific parser to process input in BIDS (IBSS) format.
    """

    __implements__ = (IBibliographyParser ,)

    meta_type = "IBSS Parser"

    format = {'name':'IBSS',
              'extension':'ibss'}

    def __init__(self,
                 id = 'bids',
                 title = "IBSS parser",
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

    def checkFormat(self, source):
        """
        is this my format?
        """
        #raise Exception(type(source))
        if source.find('      AU: ') > -1:
            return 1
        else:
            return 0


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
        for line in entry.readlines():
            # XXX This should be made to work when there is not indentation!
            if line[8] == ':':
                record[key] = '\n'.join(val)
                key = line[6:8]
                val = []
                val.append(line[10:].strip())
            else:
                val.append(line.strip())

        result = {}

        result['authors'] = self._parseAU(record['AU'])

        for key in key_mapping.keys():
            if record.has_key(key):
                result[key_mapping[key]] = record[key]

        try:
            if record.has_key('JN'):
                result['reference_type'] = 'ArticleReference'
                r = self._parseJN(record['JN'])
            elif record.has_key('BN'):
                if record['DT'] == 'Chapter':
                    result['reference_type'] = 'InbookReference'
                    #r = self._parseBNCH(record['BN'])
                else:
                    result['reference_type'] = 'BookReference'
                r = self._parseBN(record['BN'])

            for key in parse_key_list:
                if r.has_key(key):
                    result[key] = r[key]
        except ParseException:
            # can be thrown by the _parseXX methods too
            # Must catch TypeError to stop it propagating up to masquerade as a checkFormat error <grr />
            entry.seek(0)
            result = EntryParseError(entry.read().replace('\n', '\\n'))
        except TypeError:
            entry.seek(0)
            result = EntryParseError('TYPEERROR: %s' % entry.read().replace('\n', '\\n'))

        return result

    def _parseAU(self, s):
        # e.g. 'Diermeier_D, Eraslan_H, Merlo_A'
        d = []
        s = s.replace('\n', ' ')
        l = s.split(', ')
        for person in l:
            p = {}
            p['lastname'], inits = person.split('_')
            if len(inits) > 1:
                p['firstname'] = inits[0]
                p['middlename'] = inits[1:]
            else:
                p['firstname'] = inits
            d.append(p)
        return d

    def _parseJN(self, s):
        # e.g.
        #   'Journal of politics, May 2002, Vol.64, No.2, pp.491-509'
        # or
        #   'National Institute economic review, Jan 2000, No.171, pp.94-105'
        # or
        #   'British journal of political science, Apr 1979, Vol.9(2), pp.129-156'
        d = {}
        s = s.replace('\n', ' ')
        p = pp_re.search(s)
        if p is None:
            p = p_re.search(s)
        if p is None:
            p = p_re2.search(s)
        if p is not None:
            d['pages'] = p.groups()[0]
        else:
            d['pages'] = ''
        p = vol_no_re.search(s)
        if p is not None:
            d['volume'] = p.groups()[0]
            d['number'] = p.groups()[1]
        else:
            p = vol_re.search(s)
            if p is not None:
                d['volume'] = p.groups()[0]
            else:
                d['volume'] = ''
            p = no_re.search(s)
            if p is not None:
                d['number'] = p.groups()[0]
            else:
                d['number'] = ''
        p = month_year_re.search(s)
        if p is not None:
            d['publication_month'] = p.groups()[0]
            d['publication_year'] = p.groups()[1]
            s = s[:p.span()[0]].strip()
        else:
            p = year_re.search(s)
            if p is not None:
                d['publication_year'] = p.groups()[-1]
                s = s[:p.span()[0]].strip()
        d['journal'] = s
        return d

    def _parseBN(self, s):
        # e.g.
        #   Economics and politics - the calculus of support, The
        #   University of Michigan Press, Ann Arbor, M.I., 1991. pp.141-160
        # or
        #   Public support for market reforms in new democracies, Cambridge
        #   University Press, Cambridge, New York, 2001
        # or
        #   Inside local government: a case for radical reform, S. Browne, London, 1984. 414p.
        # or
        #   Party government in 48 democracies (1945-1998): composition,
        #   duration, personnel, Kluwer Academic Publishers, Dordrecht,
        #   Boston MA, 2000. xii, 580p.
        # I don't know how to deal with the latter.  Splitting on commas doesn't work :-(
        b = {}
        s = s.replace('\n', ' ')
        p = p_re.search(s)
        if p is None:
            p = pp_re.search(s)
        if p is not None:
            b['pages'] = p.groups()[0]
        else:
            b['pages'] = ''
        p = year_re.search(s)
        # Strip off what we've already extracted while we're at the next step.
        if p is not None:
            b['publication_year'] = p.groups()[-1]
            s = s[:p.span()[0]].strip()
            #raise Exception(s)
        else:
            year = s[-4:]
            if year.isalnum():
                b['publication_year'] = year
                s = s[:-4].strip()
            else:
                b['publication_year'] = ''
        if s[-1] == ',':
            s = s[:-1]
        l = s.split(', ')
        # XXX Some assumptions are made now, and they may not always be right!
        if len(l) == 4:
            # Assumes (I think the more common case) s looks like the first 2 examples above.
            b['booktitle'] = l[0]
            b['publisher'] = l[1]
            b['address'] = ', '.join( (l[2], l[3]) )
        elif len(l) == 3:
            # Assumes s looks like the 3rd example above
            b['booktitle'] = l[0]
            b['publisher'] = l[1]
            b['address'] = l[2]
        elif len(l) > 4:
            b['address'] = l.pop()
            b['publisher'] = l.pop()
            b['booktitle'] = ', '.join(l)
        else:
            raise ParseException()
        return b

InitializeClass(IBSSParser)


def manage_addIBSSParser(self, REQUEST=None):
    """ """
    try:
        self._setObject('ibss', IBSSParser())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)

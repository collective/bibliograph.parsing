############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""MedlineParser class"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from bibliograph.parsing.parsers.base \
     import IBibliographyParser, BibliographyParser

import re


class MedlineParser(BibliographyParser):
    """
    A specific parser to process input in Medline-format.
    """

    __implements__ = (IBibliographyParser ,)

    meta_type = "Medline Parser"

    format = {'name':'Medline',
              'extension':'med'}

    def __init__(self,
                 id = 'medline',
                 title = "Medline parser",
                 delimiter = '\n\n',
                 pattern = r'(^.{0,4}- )',
                 flag = re.M):
        """
        initializes including the regular expression patterns
        """
        self.id = id
        self.title = title
        self.setDelimiter(delimiter)
        self.setPattern(pattern, flag)


    # Here we need to provide 'checkFormat' and 'parseEntry'

    def checkFormat(self, source):
        """
        is this my format?
        """
        # vanilla test for 'PMID- ' in the sub-string 'source[0, 100]'
        ## rr: can definitively be improved

        if source.find('PMID- ', 0, 1000) > -1:
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

        tokens = self.pattern.split(entry)

        checkAU = 0
        if 'FAU - ' not in tokens:
            checkAU = 1

        nested = []
        for i in range(1,len(tokens),2):
            nested.append([tokens[i],tokens[i+1]])

        # some defaults
        result['note'] = 'automatic medline import'

        for key, value in nested:
            if key == 'PT  - ' and (value.find('Journal Article')> -1
                                    or value.find('JOURNAL ARTICLE')> -1):
                result['reference_type'] = 'ArticleReference'
            elif key == 'TI  - ':
                title = value.replace('\n', ' ').replace('      ', '').strip()
                result['title'] = title
            elif key == 'AB  - ':
                tmp = value.replace('\n', ' ').replace('  ', '')
                result['abstract'] = tmp.replace('  ', '').replace('  ', '')
            elif key == 'PMID- ': result['pmid'] = str(value).strip()
            elif key == 'TA  - ': result['journal'] = str(value).strip()
            elif key == 'VI  - ': result['volume'] = str(value).strip()
            elif key == 'IP  - ': result['number'] = str(value).strip()
            elif key == 'PG  - ': result['pages'] = str(value).strip()
            elif key == 'DP  - ':
                result['publication_year'] = value[:4]
                pmonth = value[5:].replace('\n','').replace('\r','')
                result['publication_month'] = pmonth
            elif key == 'FAU - ':
                raw = value.replace('\n', '').split(', ')
                lname = raw[0]
                fnames = raw[1].split(' ',1)
                fname = fnames[0]
                if len(fnames)> 1:
                    minit = fnames[1]
                else:
                    minit = ''
                adict = {'firstname': fname
                         ,'middlename': minit
                         ,'lastname': lname
                         }
                result.setdefault('authors',[]).append(adict)

            elif checkAU and key == 'AU  - ':
                raw = value.replace('\n', '').split()
                lname = raw[0]
                fnames = raw[1]
                fname = fnames[0]
                if len(fnames)> 1:
                    minit = fnames[1:]
                else:
                    minit = ''
                adict = {'firstname': fname
                         ,'middlename': minit
                         ,'lastname': lname
                         }
                result.setdefault('authors',[]).append(adict)

        return result

InitializeClass(MedlineParser)


def manage_addMedlineParser(self, REQUEST=None):
    """ """
    try:
        self._setObject('medline', MedlineParser())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')


    return self.manage_main(self, REQUEST)

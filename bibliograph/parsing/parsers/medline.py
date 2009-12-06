############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""MedlineParser class"""
import re

from bibliograph.core.content import Author
from bibliograph.core.content import Identifier
from bibliograph.core.content import Pages
from bibliograph.core.content import Volume
from bibliograph.core.content import WithinVolume
from bibliograph.core.content import Address
from bibliograph.core.content import BibliographicReference
from bibliograph.core.content import ArticleReference
from bibliograph.core.content import BookReference
from bibliograph.core.content import BookletReference
from bibliograph.core.content import ConferenceReference
from bibliograph.core.content import InbookReference
from bibliograph.core.content import IncollectionReference
from bibliograph.core.content import InproceedingsReference
from bibliograph.core.content import ManualReference
from bibliograph.core.content import MiscReference
from bibliograph.core.content import MasterthesisReference
from bibliograph.core.content import PhdthesisReference
from bibliograph.core.content import ProceedingsReference
from bibliograph.core.content import TechreportReference
from bibliograph.core.content import UnpublishedReference
from bibliograph.core.content import WebpublishedReference

from bibliograph.parsing.parsers.base import BibliographyParser


class MedlineParser(BibliographyParser):
    """
    A specific parser to process input in Medline-format.
    """

    format = {'name':'Medline',
              'extension':'med'}

    def __init__(self,
                 id = 'medline',
                 title = 'Medline Parser',
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
        super(MedlineParser, self).__init__()

    # Here we need to provide 'checkFormat' and 'parseEntry'

    def checkFormat(self, source):
        """
        is this my format?
        """
        # Medlines tags are up to for caps in length (padded) followed w/ a '-'
        pattern = re.compile('^[A-Z| ]{4}-', re.M)
        all_tags = re.findall(pattern, source)

        # Should always contain 'PMID-', have at least one author 'AU',
        # an abstract 'AB' and a title 'TI'
        required = ('AB  -', 'AU  -', 'PMID-', 'TI  -')
        if len(all_tags) and \
                reduce(lambda i, j: i and j, [r in all_tags for r in required]):
            return 1
        else:
            return 0

    def parseEntry(self,
                   entry,
                   author=Author,
                   identifier=Identifier,
                   article=ArticleReference,
                   book=BookReference,
                   booklet=BookletReference,
                   conference=ConferenceReference,
                   inbook=InbookReference,
                   incollection=IncollectionReference,
                   inproceedings=InproceedingsReference,
                   manual=ManualReference,
                   misc=MiscReference,
                   masterthesis=MasterthesisReference,
                   phdthesis=PhdthesisReference,
                   preprint=UnpublishedReference,
                   proceedings=ProceedingsReference,
                   techreport=TechreportReference,
                   unpublished=UnpublishedReference,
                   webpublished=WebpublishedReference
                   ):
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
        result[u'note'] = u'automatic medline import'
        # XXX This may be wrong! This parser can currently *only* handle
        #     article references!
        result[u'reference_type'] = u'ArticleReference'
        for key, value in nested:
            if 'PT' in key and (   value.find('Journal Article') > -1
                                or value.find('JOURNAL ARTICLE') > -1):
                result[u'reference_type'] = u'ArticleReference'
            elif key == 'TI  - ':
                title = value.replace('\n', ' ').replace('      ', '').strip()
                result['title'] = title
            elif key == 'AB  - ':
                tmp = value.replace('\n', ' ').replace('  ', '')
                result[u'abstract'] = tmp.replace('  ', '').replace('  ', '')
            # Must use u'pmid' (rather than 'pmid') as it gets set on the
            # IIdentifier implementation below and that requires a unicode value.
            elif key == 'PMID- ': result[u'pmid'] = value.strip()
            elif key == 'TA  - ': result[u'journal'] = value.strip()
            elif key == 'VI  - ': result[u'volume'] = value.strip()
            elif key == 'IP  - ': result[u'issue'] = value.strip()
            elif key == 'PG  - ': result[u'pages'] = value.strip()
            elif key == 'DP  - ':
                result['publication_year'] = value[:4]
                pmonth = value[5:].replace('\n','').replace('\r','')
                result['publication_month'] = pmonth
            elif key == 'FAU - ':
                raw = value.replace('\n', '').split(', ')
                lname = raw[0]
                fnames = raw[1].split(' ', 1)
                fname = fnames[0]
                if len(fnames) > 1:
                    minit = fnames[1]
                else:
                    minit = u''
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
                    minit = u''
                adict = {'firstname': fname
                         ,'middlename': minit
                         ,'lastname': lname
                         }
                result.setdefault('authors',[]).append(adict)
        # Get hold of the correct classes to use in constructing the output
        id_klass = locals().get('identifier')
        auth_klass = locals().get('author')
        reftype = result[u'reference_type'].replace(u'Reference', u'').lower()
        klass = locals().get(reftype)
        # Create the reference object from the looked-up class
        obj = klass()
        for key, value in result.items():
            if key == 'reference_type':
                # We won't set this on the returned object as it's superfluous
                # once the class/interface is correctly set.
                continue
            elif key in ('authors', 'editors'):
                for each in value:
                    author = auth_klass()
                    author.firstname = each['firstname']
                    author.middlename = each['middlename']
                    author.lastname = each['lastname']
                    if key == 'authors':
                        obj.authors.append(author)
                    else:
                        obj.isEditor = True
                        obj.editors.append(author)
            elif key in ('pmid', 'doi', 'isbn'):
                identifier = id_klass()
                identifier.id = key
                identifier.value = value
                obj.identifiers.append(identifier)
            else:
                setattr(obj, key, value)
        return obj

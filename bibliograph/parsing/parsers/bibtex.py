############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""BibtexParser class"""

# Python stuff
import re

# Bibliography stuff
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.base import BibliographyParser

from bibliograph.core.utils import _encode, _decode
from bibliograph.core.encodings import _latex2utf8enc_mapping

_encoding = 'utf-8'   # XXX: should be taken from the site configuration

class BibtexParser(BibliographyParser):
    """
    A specific parser to process input in BiBTeX-format.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IBibliographyParser, BibtexParser)
    True
    """

    meta_type = "Bibtex Parser"

    format = {'name':'BibTeX',
              'extension':'bib'}

    def __init__(self,
                 id = 'bibtex',
                 title = "BibTeX parser",
                 delimiter = '}\s*@',
                 pattern = r'(,\s*[\w\\]{2,}\s*=)'):
        """
        initializes including the regular expression patterns
        """
        self.id = id
        self.title = title
        self.setDelimiter(delimiter)
        self.setPattern(pattern)
        super(BibtexParser, self).__init__()

    # Here we need to provide 'checkFormat' and 'parseEntry'
    def checkFormat(self, source):
        """
        is this my format?
        """
        pattern = re.compile('^@[A-Z|a-z]*{', re.M)
        all_tags = re.findall(pattern, source)
        if all_tags:        
            for t in all_tags:
                type = t.strip(u'@{').lower()
                if type not in (u'article', u'book', u'booklet', u'conference',
                                u'inbook', u'incollection', u'inproceedings',
                                u'manual', u'mastersthesis', u'misc',
                                u'phdthesis', u'proceedings', u'techreport',
                                u'unpublished', u'collection', u'patent',
                                u'webpublished'):
                    return 0
            return 1
        else:
            return 0

    def preprocess(self, source):
        """
        expands LaTeX macros
        removes LaTeX commands and special formating
        converts special characters to their HTML equivalents
        """
        source = self.expandMacros(source)
        source = self.stripComments(source)
        source = self.convertChars(source)
        # it is important to convertChars before stripping off commands!!!
        # thus, whatever command will be replaced by a unicode value... the
        # remaining LaTeX commands will vanish here...
        source = self.stripCommands(source)
        return source

    def expandMacros(self, source):
        source = self.expandStringMacros(source)
        # add more macro conventions here if there are any
        return source

    def expandStringMacros(self, source):
        lines = source.split('\n')
        macros = []
        sourcelns = []
        for line in lines:
            if line.find('@String') > -1:
                macros.append(line)
            else:
                sourcelns.append(line)
        source = '\n'.join(sourcelns)
        for macro in macros:
            split_on = re.compile('[{=}]+')
            raw_matches = split_on.split(macro)
            matches = [m for m in raw_matches if m not in ['', ' ', '\r']]
            # raise str(matches)
            short = matches[1].strip()
            long = matches[-1].strip()
            pattern = "\\b" + short + "\\b"
            old = re.compile(pattern)
            source = old.sub(long, source)
        return source

    def stripCommands(self, source):
        oldstyle_cmd = re.compile(r'{\\[a-zA-Z]{2,}')
        newstyle_cmd = re.compile(r'\\[a-zA-Z]+{')
        source = oldstyle_cmd.sub('{', source)
        source = newstyle_cmd.sub('{', source)
        return source

    def stripComments(self, source):

        inside_entry = False
        waiting_for_first_brace = False
        newsource = ''

        for idx in range(len(source)):

            char = source[idx]
            last_char = (idx > 0) and source[idx-1] or '\n'
            next_char = (idx < len(source)-1) and source[idx+1] or '\n'

            if char == '@' and not inside_entry:
                inside_entry = True
                waiting_for_first_brace = True
                braces_nesting_level = 0

            if inside_entry:

                newsource = newsource + char
                if char == '{' and last_char != "\\":
                    braces_nesting_level += 1

                if char == '}' and last_char != "\\":
                    braces_nesting_level -= 1

                if waiting_for_first_brace and (braces_nesting_level == 1):
                    waiting_for_first_brace = False

                if (braces_nesting_level == 0) and not waiting_for_first_brace and (char == '}'):
                    inside_entry = False
                    newsource = newsource + "\n"

        completely = re.compile('.*')
        ## this line caused issue #20, leaving it here for now... mg-20061023
        # source = completely.sub(newsource, 'dummy')
        ## this line fixes issue #20
        source = newsource
        return source

    def convertChars(self, source):
        source = self.convertLaTeX2Unicode(source)
        source = self.fixWhiteSpace(source)
        return self.explicitReplacements(source)

    def convertLaTeX2Unicode(self, source):
        #source = _decode(source)
        for latex_entity in _latex2utf8enc_mapping.keys():
            source = source.replace(latex_entity,
                                    _latex2utf8enc_mapping[latex_entity])
        #return _encode(source)
        return source

    def fixWhiteSpace(self, source):
        ttable = [(r'\ ', ' '),
                  (r'\!', ' '),
                  ]
        source = self.mreplace(source, ttable)
        wsp_tilde = re.compile(r'[^/\\]~')
        return wsp_tilde.sub(self.tilde2wsp, source).replace('\~', '~')

    def tilde2wsp(self, hit):
        return hit.group(0)[0] + ' '

    def explicitReplacements(self, source):
        # list of 2 tuples; second element replaces first
        ttable = [(r'\/', ''),
                  (r'\&', '&'),
                  (r'\~', '~'),
                  (r'---', '&mdash;'),
                  (r'--', '&ndash;'),
                  ]
        return self.mreplace(source, ttable)

    def mreplace(self, s, ttable):
        for a, b in ttable:
            s = s.replace(a, b)
        return s

    # done with preprocessing

    def parseEntry(self, entry):
        """
        parses a single entry

        returns a dictionary to be passed to
        BibliographyEntry's edit method
        """
        # remove newlines and <CR>s, and remove the last '}'
        entry = entry.replace('\n', ' ').replace('\r', '').replace('\t', ' ').rstrip().rstrip('}')
        tokens = self.pattern.split(entry)
        try:
            reftype, pid = tokens[0].strip().split('{')
            reftype = reftype.replace('@', '').strip().lower()
        except:
            return "Bibtex Parser Error: malformed first line."
        # Get hold of the correct classes to use in constructing the output
        id_klass = self.class_outputs['identifier']
        klass = self.class_outputs[reftype]
        # Create the reference object from the looked-up class
        obj = klass()
        # Iterate over the key/value pairs from the bibtex
        for k,v in self.group(tokens[1:],2):
            key = k[1:-1].strip().lower()
            v = self.clean(v.rstrip().rstrip(',').rstrip())
            # INBOOKs mapping: title -> booktitle, chapter -> chapter and title
            if reftype in ('inbook', 'incollection'):#, 'inproceedings'):
                if key in ('title', 'booktitle'):
                    key = 'volumetitle'
                if key == 'chapter':
                    key = 'title'
            # special procedure for authors and editors
            if key == 'author':
                [obj.authors.append(auth) for auth in self.parseAuthors(v, isEditor=False)]
            elif key == 'editor' and reftype in ('inbook', 'incollection', 'inproceedings'):
                [obj.editors.append(auth) for auth in self.parseAuthors(v, isEditor=True)]
            elif key == 'year':
                obj.publication_year = v
            elif key == 'month':
                obj.publication_month = v
            elif key == 'number':
                obj.issue = v
            elif (key == 'keywords'):
                #if result.has_key('keywords'):
                #    result[key].append(v)
                #else:
                #    result[key] = [ v, ]
                # XXX We don't handle this at the moment as they should, perhaps
                #     be mapped to plone keywords
                pass
            elif key in ('doi', 'isbn', 'pmid'):
                # These are 'identifiers'...
                idobj = id_klass()
                idobj.id = key
                idobj.value = v
                obj.identifiers.append(idobj)
            else:
                setattr(obj, key, v)
        # do some renaming and reformatting
        tmp = obj.note
        while tmp and tmp[-1] in ['}', ',', '\n', '\r']:
            tmp = tmp[:-1]
        if tmp:
            obj.note = tmp
        tmp = obj.title
        for car in ('\n', '\r', '\t'):
            tmp = tmp.replace(car, ' ')
        while '  ' in tmp:
            tmp = tmp.replace('  ', ' ')
        obj.title = tmp
        return obj

    # the helper method's

    def splitAuthor(self, author=None):
        if not author:
            return []
        #parts = author.replace('.', ' ').split(',',1)
        parts = author.split(',',1)
        if len(parts) == 1:
            return parts[0].split()
        else:
            tmp = parts[1].split()
            tmp.append(parts[0])
            return tmp

    def parseAuthors(self, value, isEditor=False):
        authors = []
        author_klass = self.class_outputs['author']
        value = value.replace(' AND', ' and')
        authorlist = value.split(' and')
        for author in authorlist:
            fname = mname = lname = u''
            parts = self.splitAuthor(author)
            if len(parts) == 1:
                lname = parts[0].strip()
            else:
                lname = parts[-1].strip()
                fname = parts[0].strip()
                if parts[1:-1]:
                    for part in parts[1:-1]:
                        mname = mname + part.strip()
            authobj = author_klass()
            authobj.firstname = fname
            authobj.middlename = mname
            authobj.lastname = lname
            authobj.isEditor = isEditor
            authors.append(authobj)
        return authors

    def clean(self, value):
        value = value.replace('{', '').replace('}', '').strip()
        if value and value[0] == '"' and len(value) > 1:
            value = value[1:-1]
        return value

    def group(self, p,n):
        """ Group a sequence p into a list of n tuples."""
        mlen, lft = divmod(len(p), n)
        if lft != 0: mlen += 1

        # initialize a list of suitable length
        lst = [[None]*n for i in range(mlen)]

        # Loop over all items in the input sequence
        for i in range(len(p)):
            j,k = divmod(i,n)
            lst[j][k] = p[i]

        return map(tuple, lst)

############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""BibtexParser class"""

import os
import re

from zope.component import getUtility, ComponentLookupError

from bibliograph.parsing.parsers.base import BibliographyParser
from bibliograph.rendering.interfaces import IBibTransformUtility

from bibliograph.core.utils import _encode, _decode
from bibliograph.core.bibutils import _hasCommands
from bibliograph.core.encodings import _latex2utf8enc_mapping
from bibliograph.core.encodings import _latex2utf8enc_mapping_simple


_encoding = 'utf-8'   # XXX: should be taken from the site configuration
haveBibUtils = _hasCommands('bib2xml')
FIX_BIBTEX = os.environ.has_key('FIX_BIBTEX')

class BibtexParser(BibliographyParser):
    """
    A specific parser to process input in BiBTeX-format.
    """

    meta_type = "Bibtex Parser"

    format = {'name':'BibTeX',
              'extension':'bib'}

    def __init__(self,
                 id = 'bibtex',
                 title = "BibTeX parser",
                 delimiter = '}\s*@',
                 pattern = '(,\s*[\w\-]{2,}\s*=)'):
        """
        initializes including the regular expression patterns
        """
        self.id = id
        self.title = title
        self.setDelimiter(delimiter)
        self.setPattern(pattern)


    # Here we need to provide 'checkFormat' and 'parseEntry'
    def checkFormat(self, source):
        """
        is this my format?
        """
        pattern = re.compile('^@[A-Z|a-z]*{', re.M)
        all_tags = re.findall(pattern, source)

        if all_tags:
            for t in all_tags:
                type = t.strip('@{').lower()
                if type not in ('article','book','booklet','conference','inbook','incollection',
                                'inproceedings','manual','mastersthesis','misc','phdthesis',
                                'proceedings','techreport','unpublished','collection','patent',
                                'webpublished'):
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

        # let Bibutils cleanup up the BibTeX mess
        if FIX_BIBTEX and haveBibUtils:
            try:
                tool = getUtility(IBibTransformUtility, name=u"external")
                source = tool.transform(source, 'bib', 'bib')
            except ComponentLookupError:
                pass

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
        for latex_entity in _latex2utf8enc_mapping_simple.keys():
            source = _encode(_decode(source).replace(latex_entity, _latex2utf8enc_mapping_simple[latex_entity]))

        for latex_entity in _latex2utf8enc_mapping.keys():
            source = _encode(_decode(source).replace(latex_entity, _latex2utf8enc_mapping[latex_entity]))

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
        result = {}
        authorlist = []
        authorURLlist = []

        # remove newlines and <CR>s, and remove the last '}'
        entry = entry.replace('\n', ' ').replace('\r', '').replace('\t', ' ').rstrip().rstrip('}')
        tokens = self.pattern.split(entry)
        try:
            type, pid = tokens[0].strip().split('{')
            type = type.replace('@', '').strip().lower()
            result['reference_type'] = type.capitalize() + 'Reference'
            result['pid'] = pid.replace(',', '').strip()
        except:
            return "Bibtex Parser Error: malformed first line."

        for k,v in self.group(tokens[1:],2):
            key = k[1:-1].strip().lower()
            # INBOOKs mapping: title -> booktitle, chapter -> chapter and title
            if type == 'inbook':
                if key == 'title':
                    key = 'booktitle'

                if key == 'chapter':
                    result['title'] = self.cleanLine(v)

            # BibTex field "type" maps to CMFBAT field "publication_type"
            if key == 'type':
                key = 'publication_type'
                result[key] = self.cleanLine(v)

            # special procedure for authors and editors
            elif key == 'author':
                if result.has_key('author'):
                    result[key].append(self.cleanLine(v))
                else:
                    result[key] = [ self.cleanLine(v) ]
            elif (key == 'editor') and (type in ['book','proceedings']):
                if result.has_key('editor'):
                    result[key].append(self.cleanLine(v)) 
                else:
                    result[key] = [self.cleanLine(v)]
            elif key == 'keywords':
                if not result.has_key(key):
                    # Original BibTeX files contain only *one* 'keywords = '
                    # for multiple keywords
                    result[key] = self.splitMultiple(v) 
                else:
                    # This is likely used by other importers/parser trying to mis-use
                    # the BibTeX importer with multiple keywords
                    result[key].append(self.cleanLine(v))
            else:
                value = self.cleanLine(v)
                result[key] = value
                # Aliasing the value to an upper-cased key so that when this dictionary
                # is passed into <a_reference_object>.edit(**dictionary), the values
                # will match and auto-update schema fields that are specified in either
                # upper or lower case.  This is motivated by the 'DOI' field being upper-cased.
                # Of course, this won't help mixed-case fields, but we'd probably need to change
                # Archetype internals to fix that - and that would be a questionable endeavour.
                result[key.upper()] = value

            #print key, result[key]

        # compile authors list of dictionaries
        # we can have authors
        if result.has_key('author'):
            for each in result['author']:
                each = each.replace(' AND', ' and')
                authorlist.extend( each.split(' and') )
        # but for some bibref types we can have editors alternatively
        elif result.has_key('editor') and (type in ['book','proceedings']):
            result['editor_flag'] = True
            for each in result['editor']:
                each = each.replace(' AND', ' and')
                authorlist.extend( each.split(' and') )
        if result.has_key('authorURLs'):
            authorURLlist = result['authorURLs'].split('and ')

        if authorlist:
            alist = []
            authorlist = [x for x in authorlist if x]
            for author in authorlist:
                fname = mname = lname = ''
                parts = self.splitAuthor(author)
                if len(parts) == 1:
                    lname = parts[0].strip()
                else:
                    lname = parts[-1].strip()
                    fname = parts[0].strip()
                    if parts[1:-1]:
                        for part in parts[1:-1]:
                            mname = mname + part.strip()
                adict = {'firstname': fname,
                         'middlename': mname,
                         'lastname': lname}
                alist.append(adict)

        if authorURLlist and alist:
            index = 0
            for url in authorURLlist:
                alist[index]['homepage'] = url.strip()
                index += 1

        if authorlist:
            result['authors'] = alist

        # do some renaming and reformatting
        tmp = result.get('note')
        while tmp and tmp[-1] in ['}', ',', '\n', '\r']:
            tmp = tmp[:-1]
        if tmp:
            result['note'] = tmp
        result['publication_year'] = result.get('year', '')
        result['publication_month'] = result.get('month', '')
        result['publication_url'] = result.get('url', '')
        ## result['publication_title'] = result.get('title', '')
        tmp = result.get('title','')
        for car in ('\n', '\r', '\t'):
            tmp = tmp.replace(car, ' ')
        while '  ' in tmp:
            tmp = tmp.replace('  ', ' ')
        result['title'] = tmp

        # collect identifiers
        identifiers = list()
        for key in ('isbn', 'doi', 'asin', 'purl', 'urn', 'issn'):
            if key in result:
                identifiers.append({'label' : key.upper(), 'value': result[key]})
        if identifiers:
            result['identifiers'] = identifiers

        return result

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

    def splitMultiple(self, value):
        value = self.clean(value)
        result = list()
        for item in value.split(','):
            item = item.strip()
            if item:
                result.append(item)
        return result

    def clean(self, value):
        value = value.replace('{', '').replace('}', '').strip()
        if value and value[0] == '"' and len(value) > 1:
            value = value[1:-1]
        return value

    def cleanLine(self, value):
        return self.clean(value.rstrip().rstrip(',').rstrip())

    def group(self, p,n):
        """ Group a sequence p into a list of n tuples."""
        mlen, lft = divmod(len(p), n)
        if lft != 0: 
            mlen += 1

        # initialize a list of suitable length
        lst = [[None]*n for i in range(mlen)]

        # Loop over all items in the input sequence
        for i in range(len(p)):
            j,k = divmod(i,n)
            lst[j][k] = p[i]

        return map(tuple, lst)

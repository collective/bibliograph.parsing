############################################################################
#                                                                          #
#             copyright (c) 2004 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""pybliographer's BibtexParser class"""

# Python stuff
import re, os
from types import StringTypes

# pybliographer stuff
HAS_PYBLIOGRAPHER = 1
try:
    import _bibtex
except ImportError:
    HAS_PYBLIOGRAPHER = 0

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from Products.CMFBibliographyAT.tool.parsers.base \
     import IBibliographyParser, BibliographyParser


class PyBlBibtexParser(BibliographyParser):
    """
    A specific parser to process input in BiBTeX-format.
    """

    __implements__ = (IBibliographyParser ,)

    meta_type = "Pybliographers Bibtex Parser"

    format = {'name':'BibTeX (pybl)',
              'extension':'bib'}

    def __init__(self,
                 id = 'pyblbibtex',
                 title = "Pybliographers BibTeX parser",
                 delimiter = '(~\s*$)*',
                 pattern = '(,\s*\w{2,}\s*=)'):
        """
        initializes including the regular expression patterns
        """
        self.id = id
        self.title = title
        self.setDelimiter(delimiter)
        self.setPattern(pattern)


    # Here we need to provide 'checkFormat' and 'parseEntry'
    # FIXME TODO - refactor with bibtex
    def checkFormat(self, source):
        """
        is this my format?
        """
        # vanilla test for 'author' or 'editor'
        # in the sub-string 'source[10, 100]'
        ## rr: can definitively be improved

        teststring = source[10:100].lower()
        ai = teststring.find('author')
        ei = teststring.find('editor')
        if ai + ei > -2:
            return 1
        else:
            return 0

    def preprocess(self, source):
        """
        expands LaTeX macros
        """
        return self.expandMacros(source)

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
            short = matches[1].strip()
            long = matches[-1].strip()
            pattern = "\\b" + short + "\\b"
            old = re.compile(pattern)
            source = old.sub(long, source)
        return source

    def getEntries(self, source):
        """
        main method to be called for parsing the entries
        in 'source' - a string representation of the source file
        """
        source = self.preprocess(source) # would pybliographer do that anyway?
        file = self.toBibIO(source)
        raw_entries = self.parsedEntries(file)
        return self.mapp_entries(raw_entries)

    def parsedEntries(self, file):
        """the main routine from pybliographer"""
        def expand (file, entry):
            items = entry [4]
            for k in items.keys ():
                items [k] = _bibtex.expand (file, items [k], -1)
            return
        results = []
        while 1:
            try:
                entry = _bibtex.next (file)
                if entry is None: break
                expand (file, entry)
                results.append(entry)
##                 obtained = `entry`
            except IOError, msg:
                obtained = 'ParserError'
        return results

    def toBibIO(self, source):
        """ugly hack to get a bibtex file object"""
        wdir = self._makeWorkingDirectory()
        return self._makeBibFile(wdir, source)

    def _makeWorkingDirectory(self, path=None):
        if not path:
            path = '/tmp/bib-tool'
        try:
            os.mkdir(path)
        except OSError:
            pass
        return path

    def _makeBibFile(self, work_dir, source):
        full_path = os.path.join(work_dir, 'tmp.bib')
        tmp = open(full_path, 'wb')
        tmp.write(source)
        tmp.close()
        return _bibtex.open_file(full_path, 0) # 0: the 'strict' parameter

    def mapp_entries(self, entries):
        """
        turns a list of _bibtex entry objects into a list of dictionaries
        """
        return [self.mapp_entry(entry) for entry in entries]

    def mapp_entry(self, entry):
        """
        turn _bibtex's entry object into a simple dictionary
        to be passed to BibliographyEntry's edit method
        """
        result = {}
        authorlist = authorURLlist = []

        result['pid'] = entry[0]
        result['reference_type'] = entry[1].capitalize() + 'Reference'

        raw_items = entry[4]

        for key in raw_items.keys():
            result[key] = self.fixEncoding(raw_items[key][2])

        if raw_items.has_key('author'):
            result['authors'] = self.makeAuthorList(raw_items['author'][3])

        if raw_items.has_key('authorurls'):
            authorURLlist = result['authorurls'].split('and ')
            index = 0
            for url in authorURLlist:
                # restore a potentially lost tilde
                url = url.strip().replace(' ','~')
                result['authors'][index]['homepage'] = url
                index += 1

        # some renaming
        result['publication_year'] = result.get('year', '')
        result['publication_month'] = result.get('month', '')
        result['publication_url'] = result.get('url', '').replace(' ', '~')

        return result

    def fixEncoding(self, text):
        """primitive (not fool prove) test to ensure utf-8 encoding"""
        if type(text) not in StringTypes:
            return text
        target_enc = 'utf-8' # replace with site encoding
        if type(text) == type(u''):
            return text.encode(target_enc)
        source_enc = ['ascii', 'latin-1', 'utf-8']
        for enc in source_enc:
            try:
                return unicode(text, enc).encode(target_enc)
            except UnicodeDecodeError:
                pass
        return text # unchanged if everything fails

    def makeAuthorList(self, raw_list):
        """turns the author list into a list of dictionaries"""
        alist = []
        for a in raw_list:
            adict = {'firstname':self.fixEncoding(a[1]),
                     'lastname':self.fixEncoding(a[2]),
                     }
            alist.append(adict)
        return alist


 # Class instanciation
InitializeClass(PyBlBibtexParser)


def manage_addPyBlBibtexParser(self, REQUEST=None):
    """ """
    try:
        if not HAS_PYBLIOGRAPHER:
            raise ImportError
        self._setObject('pyblbibtex', PyBlBibtexParser())
    except ImportError:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add needs ' \
            'the _bibtex module from pybliographer.',
            action='manage_main')
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The parser you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)

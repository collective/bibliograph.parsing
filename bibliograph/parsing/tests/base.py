from zope.interface import implements
from bibliograph.core.interfaces import IBibliographicReference

class TestEntries(object):
    """ For testing the parsers, this class wraps breaking the parsed
    dictionaries into TestEntry objects to simplify the testing code.
    Typically, application code will build its own entry type. 
    """

    def __init__(self, parsed_entries):
        """ Given a list of parsed entries, builds a list
        of TestEntry objects @ self.entries
        """
        self.entries = []

        # Some parsers leave list items containing notes about the 
        # parsing process - if so, toss out the notes and just hang
        # onto the entries themselves
        for e in parsed_entries:
            if len(e.keys()) > 2:
                self.entries.append(TestEntry(e))

        #for i in range(0, len(parsed_entries)-1, 2):
        #    self.entries.append(TestEntry(parsed_entries[i]))

    def __len__(self):
        return len(self.entries)

    def author_last_names(self):
        """ Returns a list of all author last names contained in 
        the respective entries.
        """
        last_names = []
        for e in self.entries:
            for a in e.authors:
                last_names.append(a['lastname'])
        return last_names

    def titles(self):
        """ Returns a list of all titles from respective entries.
        """
        return [e.title for e in self.entries]
        
    def entryByTitle(self, title):
        """ Takes a title, returns the entry which has that title, or None
        """
        for e in self.entries:
            if e.title == title:
                return e
        return None

class TestEntry(object):
    """ Intended for test purposes only - takes a parsed entry and
    generates a more logical structure for testing contents."""

    def __init__(self, kw):
        '''Expects a single parsed entry from one of the parsers.  If all
        of the required fields aren't present, an exception is raised.
        '''

        # Required fields
        required = ['authors', 'publication_month', 'publication_year',
                    'reference_type', 'title', 'volume']
        for key in required:
            try:
                setattr(self,key,kw[key])
            except Exception, e:
                raise Exception("Doesn't look like a valid parsed entry. " +
                                "Missing at least field: %s from %s (%s)" % (key, kw, e))

        # Optional fields
        for key in kw.keys():
            if key not in required:
                setattr(self,key,kw[key])


    def authorIsPresent(self, author_dict):
        """ Expects a dictionary with keys 'firstname', 'middlename', 'lastname'
            Returns true if there is an author in self.authors which matches
        """
        for a in self.authors:
            dict_same = True
            for key in a.iterkeys():
                if a[key] != author_dict[key]:
                    dict_same = False
            if dict_same == True:
                return True

        return False

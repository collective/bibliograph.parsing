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

class TestEntry(object):
    """ Intended for test purposes only - takes a parsed entry and
    generates a more logical structure for testing contents."""

    def __init__(self, kw):
        '''Expects a single parsed entry from one of the parsers.  If all
        of the required fields aren't present, an exception is raised.
        '''

        # Required fields
        for key in ['abstract', 'authors', 'number', \
                        'publication_month', 'publication_year', \
                        'reference_type', 'title', 'volume']:
            try:
                setattr(self,key,kw[key])
            except:
                raise Exception("Doesn't look like a valid parsed entry. " +
                                "Missing at least field: %s from %s" % (key,kw))

        # Optional fields
        for key in ['note', 'pages',]:
            try:
                setattr(self,key,kw[key])
            except:
                pass # optional


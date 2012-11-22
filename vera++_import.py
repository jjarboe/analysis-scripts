import re
import sys
from coverity_import import CoverityIssueCollector, main, Issue

class VeraCollector(CoverityIssueCollector):
    '''
    A simple collector for Vera++ reports.  The Vera++ analysis should use
    the -showrules option.
    '''
    _report_re = re.compile(r'^(?P<filename>.+):(?P<line>\d+):\s*\((?P<rule>.+)\) (?P<desc>.*)$', re.M)

    def process(self, f):
        '''
        This method assumes that reports are isolated to a single line.
        If your tool reports issues on multiple lines, or for some other
        reason the report lines may not be reordered, you'll need to override
        this method to handle things appropriately.
        '''
        for l in f:
            if not l.strip(): continue
            m = self._report_re.match(l)
            if m:
                msg = Issue(**m.groupdict())
                msg.add_location(msg.line, msg.filename)
                self._messages.add(msg)
                self._files.add(msg.filename)
            else:
                print 'Unrecognized input format:', l
                sys.exit(-1)

    def sources(self):
        return [{'file': f, 'encoding': 'ASCII'} for f in self._files]

    def issues(self):
        return [
        {
            'checker': 'Vera++',
            'extra': '',
            'file': i.filename,
            'function': '',
            'subcategory': i.rule,
            'events': [
                {
                'tag': i.desc,
                'description': i.desc,
                'line': i._locs[0]['line'],
                'main': True
                }
            ],
        }
        for i in self._messages]

if __name__ == '__main__':
    main(VeraCollector())

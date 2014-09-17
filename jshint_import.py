import re
import sys
import os.path
from coverity_import import CoverityIssueCollector, main, get_opts

class JSHintCollector(CoverityIssueCollector):
    '''
    A simple collector for JSHint reports.  The following options are not
    currently supported: --verbose, --show-non-errors
    '''
    # A normal error line
    _report_re = re.compile(r'^(?P<file>.+):\s+line\s+(?P<line>\d+),\s+(?P<description>.*)$', re.M | re.I)

    # The summary line at the end, which just counts the findings
    _summary_re = re.compile(r'^\s*\d+\s+errors.*$', re.M | re.I)

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
                f = m.groupdict()
                msg = self.create_issue(checker='JSHint',
                            tag = f['description'],
                            description = f['description'],
                            subcategory = 'Error',
                           )
                msg.add_location(f['line'], f['file'])
                self.add_issue(msg)
            elif self._summary_re.match(l):
                pass
            else:
                print 'Unrecognized input format:', l
                sys.exit(-1)

if __name__ == '__main__':
    opts = get_opts('jshint_import.py', sys.argv)
    print JSHintCollector(**opts).run(sys.argv[-1])

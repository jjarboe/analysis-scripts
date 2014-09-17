import re
import sys
import os.path
from coverity_import import CoverityIssueCollector, main, get_opts

class VeraCollector(CoverityIssueCollector):
    '''
    A simple collector for Vera++ reports.  The Vera++ analysis should use
    the following options:
      --show-rule
      --no-duplicate

    In addition, we recommend the following options:
    -R L003 -R L004 -R L005 -R L006 -R T008 -R T011 -R T012 -R T019
    '''
    _report_re = re.compile(r'^(?P<file>.+):(?P<line>\d+):\s*\((?P<subcategory>.+)\) (?P<description>.*)$', re.M)

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
                msg = self.create_issue(checker='Vera++',
                            tag = f['subcategory'],
                            description = f['description'],
                            subcategory = f['subcategory']
                           )
                msg.add_location(f['line'], f['file'], f['description'])
                self.add_issue(msg)
            else:
                print 'Unrecognized input format:', l
                sys.exit(-1)

if __name__ == '__main__':
    opts = get_opts('vera++_import.py', sys.argv)
    print VeraCollector(**opts).run(sys.argv[-1])

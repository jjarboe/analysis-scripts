import re
import sys
import os.path
from coverity_import import CoverityIssueCollector, main, Issue

class VeraCollector(CoverityIssueCollector):
    '''
    A simple collector for Vera++ reports.  The Vera++ analysis should use
    the -showrules option.
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
                msg = Issue(checker='Vera++',
                            tag = f['description'],
                            description = f['description'],
                            subcategory = f['subcategory'],
                           )
                print '###', self._build_dir
                msg.add_location(f['line'], os.path.join(self._build_dir,f['file']))
                self._issues.add(msg)
                self._files.add(f['file'])
            else:
                print 'Unrecognized input format:', l
                sys.exit(-1)

if __name__ == '__main__':
    print VeraCollector(build_dir='/').run(sys.argv[-1])

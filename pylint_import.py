from coverity_import import CoverityIssueCollector, get_opts
import re
import os.path
import sys

class PyLintCollector(CoverityIssueCollector):
    '''
    A simple collector for PyLint reports.
    The PyLint analysis should be run with the following options:

    -r n
    --msg-template="{path}:{line}: ({msg_id}) {symbol}: {obj}: {msg}"

    In addition, we recommend the following options:

    -d C0103,C0301,C0330,C0111,W0401,W0614
    '''

    _report_re = re.compile(r'^(?P<file>.+?):(?P<line>\d+):\s*\[(?P<subcategory>.+?)\((?P<tag>.+?)\), (?P<function>.*)\] (?P<description>.+)$', re.M)

    def process(self, f):
        '''
        This method assumes that reports are isolated to a single line.
        If your tool reports issues on multiple lines, or for some other
        reason the report lines may not be reordered, you'll need to
        override this method to handle things appropriately.
        '''

        for l in f:
            l = l.strip()
            if not l: continue

            # Pylint marks the start of a module with a line like **** <module>
            if l.startswith('*****'): continue

            m = self._report_re.match(l)
            if m:
                f = m.groupdict()
                msg = self.create_issue(checker = 'PyLint.'+f['tag'],
                            tag = f['tag'],
                            description = f['description'],
                            function = f['function'],
                            subcategory = f['subcategory']
                           )
                msg.add_location(f['line'], f['file'], f['description'])
                self.add_issue(msg)
            else:
                # Pylint inserts code snippets for some issues; skip those lines
                pass
                #print 'Unrecognized input format:', l
                #sys.exit(-1)

if __name__ == '__main__':
    opts = get_opts('pylint_import.py', sys.argv)
    print PyLintCollector(**opts).run(sys.argv[-1])

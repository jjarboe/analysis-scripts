from coverity_import import CoverityIssueCollector, main, get_opts

import xml.etree.ElementTree as ET

class CppCheckCollector(CoverityIssueCollector):
    '''
    A simple collector for cppcheck reports.  The cppcheck analysis should use
    the --xml-version=2 option, and we recommend the following additional
    options: --enable=all --suppress=missingIncludeSystem
    '''

    _checker_prefix = 'cppcheck'

    def process(self, f):
        tree = ET.parse(f)
        root = tree.getroot()
        for e in root.findall('./errors/error'):
            a = e.attrib
            msg = self.create_issue(
                       checker = a['id'],
                       subcategory = a['severity'],
                       tag = a['msg'],
                       description = a['verbose']
                       )
            for loc in e.findall('location'):
                msg.add_location(loc.attrib['line'], loc.attrib['file'], loc.attrib.get('description'))
            self.add_issue(msg)

if __name__ == '__main__':
    import sys
    opts = get_opts('cppcheck_import.py', sys.argv)
    print CppCheckCollector(**opts).run(sys.argv[-1])

from coverity_import import CoverityIssueCollector, main, Issue

import xml.etree.ElementTree as ET

class CppCheckCollector(CoverityIssueCollector):
    '''
    A simple collector for cppcheck reports.  The cppcheck analysis should use
    the --xml-version=2 option.
    '''

    _checker_prefix = 'cppcheck'

    def process(self, f):
        tree = ET.parse(f)
        root = tree.getroot()
        for e in root.findall('./errors/error'):
            a = e.attrib
            msg = Issue(
                       checker = a['id'],
                       subcategory = a['severity'],
                       tag = a['msg'],
                       description = a['verbose']
                       )
            for loc in e.findall('location'):
                msg.add_location(loc.attrib['line'], loc.attrib['file'], loc.attrib.get('description'))
                self._files.add(loc.attrib['file'])
            self._issues.add(msg)

if __name__ == '__main__':
    import sys
    print CppCheckCollector().run(sys.argv[-1])

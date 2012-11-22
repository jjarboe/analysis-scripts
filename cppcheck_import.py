import re
import sys
from coverity_import import CoverityIssueCollector, main, Issue

import xml.etree.ElementTree as ET

class CppCheckCollector(CoverityIssueCollector):
    '''
    A simple collector for cppcheck reports.  The cppcheck analysis should use
    the --xml-version=2 option.
    '''

    def process(self, f):
        tree = ET.parse(f)
        root = tree.getroot()
        for e in root.findall('./errors/error'):
            msg = Issue(**e.attrib)
            for loc in e.findall('location'):
                msg.add_location(**loc.attrib)
                self._files.add(loc.attrib['file'])
            self._messages.add(msg)

    def sources(self):
        return [{'file': f, 'encoding': 'ASCII'} for f in self._files]

    def issues(self):
        return [
        {
            'checker': 'cppcheck.'+i.id,
            'extra': '',
            'file': i._locs[0]['filename'],
            'function': '',
            'subcategory': i.severity,
            'events': [
                {
                'tag': i.msg,
                'description': i.verbose,
                'line': i._locs[0]['line'],
                'main': True
                }
            ] + [
                {
                'tag': 'Related event',
                'description': i.verbose,
                'line': x['line'],
                'main': False
                }
                for x in i._locs[1:]
            ]
        }
        for i in self._messages]

if __name__ == '__main__':
    main(CppCheckCollector())

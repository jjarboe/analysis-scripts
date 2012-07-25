import re
import sys
from coverity_import import CoverityIssueCollector, main, Issue

import xml.etree.ElementTree as ET

class CheckstyleCollector(CoverityIssueCollector):
    '''
    A simple collector for cppcheck reports.  The cppcheck analysis should use
    the --xml-version=2 option.
    '''

    def process(self, f):
        tree = ET.parse(f)
        root = tree.getroot()
        for f in root.findall('file'):
            # <file name=""> ... </file>
            for e in f.findall('error'):
                # <error line="" severity="" message="" source=""/>
                a = e.attrib
                cls = a['source'].split('.')
                msg = Issue(id = '.'.join(cls[-2:]),
                            severity = a['severity'],
                            msg=cls[-1],
                            verbose=a['message']
                           )
                msg.add_location(e.attrib['line'], f.attrib['name'])
                self._files.add(f.attrib['name'])
            self._messages.add(msg)

    def sources(self):
        return [{'file': f, 'encoding': 'ASCII'} for f in self._files]

    def issues(self):
        return [
        {
            'checker': 'checkstyle.'+i.id,
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
    main(CheckstyleCollector())

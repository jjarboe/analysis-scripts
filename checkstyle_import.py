from coverity_import import CoverityIssueCollector, main, Issue

import xml.etree.ElementTree as ET

class CheckstyleCollector(CoverityIssueCollector):
    _checker_prefix='checkstyle'

    '''
    A simple collector for Checkstyle reports.
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
                msg = Issue(checker = '.'.join(cls[-2:]),
                            subcategory = a['severity'],
                            tag = cls[-1],
                            description = a['message']
                           )
                msg.add_location(e.attrib['line'], f.attrib['name'])
                self._files.add(f.attrib['name'])
                self._issues.add(msg)

if __name__ == '__main__':
    import sys
    print CheckstyleCollector().run(sys.argv[-1])

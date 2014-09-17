from coverity_import import CoverityIssueCollector, main, get_opts

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
                msg = self.create_issue(checker = '.'.join(cls[-2:]),
                            subcategory = a['severity'],
                            tag = cls[-1],
                            description = a['message']
                           )
                msg.add_location(e.attrib['line'], f.attrib['name'])
                self.add_issue(msg)

if __name__ == '__main__':
    import sys
    opts = get_opts('checkstyle_import.py', sys.argv)
    print CheckstyleCollector(**opts).run(sys.argv[-1])

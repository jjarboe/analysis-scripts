import re
import sys
from coverity_import import CoverityIssueCollector, main, Issue

import xml.etree.ElementTree as ET

class ValgrindCollector(CoverityIssueCollector):
    '''
    A simple collector for valgrind reports.  The valgrind analysis should use
    the --xml=yes option.
    '''

    def process(self, f):
        tree = ET.parse(f)
        root = tree.getroot()
        for e in root.findall('./error'):
            unique = None
            msg = None
            stack_context = None
            for c in e:
                if c.tag == 'kind':
                    id = c.text
                elif c.tag == 'unique':
                    unique = c.text
                elif c.tag == 'what':
                    verbose = c.text
                    msg = Issue(id=id, verbose=verbose, msg=verbose, function=None, unique=unique)
                    stack_context = c.tag
                elif c.tag == 'xwhat':
                    verbose = c.findtext('text')
                    msg = Issue(id=id, verbose=verbose, msg=verbose, function=None, unique=unique)
                    stack_context = c.tag
                elif c.tag == 'auxwhat':
                    verbose = c.text
                    stack_context = c.tag
                if c.tag == 'stack' and msg and stack_context:
                    if stack_context in ('auxwhat', 'xwhat'):
                        frames = c.findall('./frame')[1:2]
                    else:
                        frames = c.findall('./frame')
                    for f in frames:
                        if msg.function is None:
                            msg.function = f.findtext('./fn')
                        elif stack_context == 'what':
                            verbose = '%s called by %s' % (msg.function, f.findtext('./fn'))
                        line = f.findtext('./line')
                        file = f.findtext('./dir') + '/' + f.findtext('./file')
                        msg.add_location(line, file, description=verbose)
                        self._files.add(file)
                    self._messages.add(msg)

    def sources(self):
        return [{'file': f, 'encoding': 'ASCII'} for f in self._files]

    def issues(self):
        return [
        {
            'checker': 'valgrind',
            'extra': i.unique,
            'file': i._locs[0]['filename'],
            'function': i.function,
            'subcategory': i.id,
            'events': [
                {
                'tag': i.msg,
                'description': i._locs[0]['description'] or i.verbose,
                'file': i._locs[0]['filename'],
                'line': i._locs[0]['line'],
                'main': True
                }
            ] + [
                {
                'tag': 'Related event',
                'description': x['description'] or i.verbose,
                'file': x['filename'],
                'line': x['line'],
                'main': False
                }
                for x in i._locs[1:]
            ]
        }
        for i in self._messages]

if __name__ == '__main__':
    main(ValgrindCollector())

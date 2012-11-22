import json
import os.path

class NotImplementedException(Exception): pass
class InvalidFormatException(Exception):
    def __init__(self, msg, arg):
        self._msg = msg
        self._arg = arg

    def __str__(self):
        return '%s: "%s"' % (self._msg, self._arg)

class Issue(object):
    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k.lower(), v)
        self._locs = []

    def add_location(self, line, file):
        parts = filter(None, os.path.split(file))
        if len(parts) <= 1:
            raise InvalidFormatException('Filename must be absolute path', file)
        self._locs.append({'line':int(line), 'filename':file})

class CoverityThirdPartyIntegration(object):
    '''
    A basic wrapper that creates output appropriate for cov-import-results.
    '''
    def __init__(self, collector):
        self._collector = collector

    def dict(self):
        return {
          'header': {
                'version': 1,
                'format': 'cov-import-results input'
          },
          'sources': self._collector.sources(),
          'issues': self._collector.issues()
        }

    def output(self):
        return json.dumps(self.dict())

class CoverityIssueCollector(object):
    '''
    A basic collector for issue reports.  Not appropriate to be
    used directly; you should implement a subclass.
    '''
    def __init__(self):
        self._messages = set()
        self._files = set()

    def process(self, f):
        '''
        Process the contents of file object f.
        '''
        raise NotImplementedException('You need to implement the process() method')

    def sources(self):
        raise NotImplementedException('You need to implement the sources() method')

    def issues(self):
        raise NotImplementedException('You need to implement the issues() method')

def main(collector):
    import sys

    for fn in sys.argv[1:]:
        if fn == '-':
            collector.process(sys.stdin)
        else:
            f = open(fn,'r')
            collector.process(f)
            f.close()
 
    outputter = CoverityThirdPartyIntegration(collector)
    print outputter.output()

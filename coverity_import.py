import sys
import json
import os.path

class NotImplementedException(Exception): pass
class InvalidFormatException(Exception):
    def __init__(self, msg, arg):
        self._msg = msg
        self._arg = arg

    def __str__(self):
        return '%s: "%s"' % (self._msg, self._arg)

class IssueLocation(object):
    def __init__(self, line, filename, description):
        self.line = line
        self.filename = filename
        self.description = description

class Issue(object):
    def __init__(self, checker, tag, extra='', function='', subcategory='', description=''):
        self.checker = checker
        self.tag = tag
        self.extra = extra
        self.function = function
        self.subcategory = subcategory
        self.description = description
        self._locs = []

    def add_location(self, line, filename, description = None):
        parts = filter(None, os.path.split(filename))
        if len(parts) <= 1:
            raise InvalidFormatException('Filename must be absolute path', filename)

        self._locs.append(IssueLocation(int(line), filename, description))

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
    _checker_prefix = None
    _build_dir = None

    def __init__(self, default_encoding='ASCII', checker_prefix=None, build_dir=None):
        self._issues = set()
        self._files = set()
        self._default_encoding = default_encoding
        if checker_prefix: self._checker_prefix = checker_prefix
        if build_dir is not None: self._build_dir = build_dir

    def process(self, f):
        '''
        Process the contents of file object f.
        '''
        raise NotImplementedException('You need to implement the process() method')

    def sources(self):
        return [{'file': f, 'encoding': self._default_encoding}
                for f in self._files]

    def issues(self):
        return [
        {
            'checker': '.'.join(filter(None, [self._checker_prefix,i.checker])),
            'extra': i.extra,
            'file': i._locs[0].filename,
            'function': i.function,
            'subcategory': i.subcategory,
            'events': [
                {
                'tag': i.tag,
                'description': i._locs[0].description or i.description,
                'line': i._locs[0].line,
                'main': True
                }
            ] + [
                {
                'tag': 'Related event',
                'description': x.description or i.description,
                'line': x.line,
                'main': False
                }
                for x in i._locs[1:]
            ]
        }
        for i in self._issues]

    def run(self, *inputs):
      for fn in inputs:
        if fn == '-':
            self.process(sys.stdin)
        else:
            f = open(fn,'r')
            self.process(f)
            f.close()
 
      return CoverityThirdPartyIntegration(self).output()

def main(collector):
    print collector.run(sys.argv[1:])

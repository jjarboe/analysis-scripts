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

def normalize_path(fn):
    if fn[0].upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' and fn[1] == ':':
        fn = fn[2:]
    return fn.replace('\\','/')

class IssueLocation(object):
    def __init__(self, line, filename, description, method=None, tag=None, link=None, linktext=None):
        self.line = line
        self.filename = normalize_path(filename)
        self.description = description
        self.method = method
        self.tag = tag
        self.link = link
        self.linktext = linktext

class Issue(object):
    UNKNOWN_FILE = '?unknown?'

    def __init__(self, checker, tag, extra='', function='', subcategory='', description='', build_dir=None):
        self.main_event = 0
        self.checker = checker
        self.tag = tag
        self.extra = extra
        self.function = function
        self.subcategory = subcategory
        self.description = description
        self._locs = []
        self.filename = self.UNKNOWN_FILE
        self._build_dir = build_dir

    def add_location(self, line, filename, description=None, method=None, tag=None, link=None, linktext=None):
        if filename is not None:
            if not os.path.isabs(filename) and self._build_dir:
                filename = os.path.join(self._build_dir,filename)
            parts = filter(None, os.path.split(filename))
            if len(parts) <= 1 and filename[1] != ':':
                raise InvalidFormatException('Filename must be absolute path', filename)
            filename = normalize_path(filename)
            if self.filename == self.UNKNOWN_FILE:
                self.filename = filename

        self._locs.append(IssueLocation(int(line), filename, description, method=method, tag=tag, link=link, linktext=linktext))

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

    def create_issue(self, **kw):
        if 'build_dir' not in kw:
            kw['build_dir'] = self._build_dir
        return Issue(**kw)

    def add_issue(self, issue):
        self._issues.add(issue)
        self._files |= set([x.filename for x in issue._locs if x.filename != issue.UNKNOWN_FILE])

    def process(self, f):
        '''
        Process the contents of file object f.
        '''
        raise NotImplementedException('You need to implement the process() method')

    def sources(self):
        return [{'file': f, 'encoding': self._default_encoding}
                for f in self._files if f is not None]

    def issues(self):
        def event_obj(x, i, main_event=False):
            obj = {
                'tag': main_event and i.tag or (x.tag or 'Related event'),
                'description': x.description or i.description,
                'file': x.filename or i.filename,
                'line': x.line,
                'main': main_event
            }
            if x.link: obj['linkUrl'] = x.link
            if x.linktext: obj['linkText'] = x.linktext
            return obj

        return [
        {
            'checker': '.'.join(filter(None, [self._checker_prefix,i.checker])),
            'extra': i.extra,
            'file': i._locs[i.main_event].filename,
            'function': i.function,
            'subcategory': i.subcategory,
            'events': [
                event_obj(i._locs[i.main_event], i, True)
            ] + [
                event_obj(i._locs[x], i)
                for x in range(len(i._locs)) if x != i.main_event
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

def get_opts(myname, argv):
    if myname in argv[-1]:
        print 'usage: %s [build_dir_root] <input_file>' % (myname,)
        print 'build_dir_root: path to prepend to filenames listed in input_file, to'
        print '                ensure this script\'s output uses absolute paths.'
        print 'input_file: path to the file which this script will convert'
        sys.exit(-1)
    build_dir = ''
    if myname not in argv[-2]:
        build_dir = argv[-2]
    return {'build_dir': build_dir}

def main(collector):
    print collector.run(sys.argv[1:])

import os

from coverity_import import CoverityIssueCollector, main, Issue, InvalidFormatException

import json

class BrakemanCollector(CoverityIssueCollector):
    _checker_prefix='brakeman'

    '''
    A simple collector for Brakeman reports.
    '''

    def find_line(self, issue):
        return issue['line'] or '1'

    def process(self, f):
        data = json.load(f)
        root_dir = ''
        try:
            data['scan_info']
            data['scan_info']['brakeman_version']
            root_dir = data['scan_info']['app_path']
        except Exception, e:
            raise InvalidFormatException("Couldn't find attribute", e)

        # There are also members "ignored_warnings" and "errors"
        for issue in data.get('warnings',[]) + data.get('ignored_warnings',[]):
            # warning_type, warning_code
            # fingerprint
            # message
            # file, line, link
            # code (expression affected)
            # render_path
            # location
            #   type:controller, controller:
            #   type:method, class:, method:
            #   type:model, model:
            #   type:template, template:
            # user_input (affected variable/parameter)
            # confidence

            # Need to normalize "file" via command-line option
            if not os.path.isabs(issue['file']):
                issue['file'] = os.path.join(root_dir, issue['file'])

            attrs = {
                'checker': issue['warning_type'],
                'tag': 'Warning',
                'subcategory': issue['confidence'],
                'description': issue['message']
            }
            if issue['fingerprint']:
                attrs['extra'] = issue['fingerprint']
            if issue['location'] and issue['location'].get('method',None):
                attrs['function'] = issue['location']['class']+'.'+issue['location']['method']
            if issue['line'] is None:
                issue['line'] = self.find_line(issue)

            msg = Issue(**attrs)
            # Also takes description, method, tag, link, linktext
            msg.add_location(
                issue['line'],
                issue['file'],
                link = issue.get('link', None),
                linktext = issue.get('link') and '[Brakeman description]' or None
            )
            self._files.add(issue['file'])
            self._issues.add(msg)

if __name__ == '__main__':
    import sys
    print BrakemanCollector().run(sys.argv[-1])

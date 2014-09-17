#!/usr/bin/python
# -*- coding: utf-8 -*-
from coverity_import import CoverityIssueCollector, main, get_opts

import xml.etree.ElementTree as ET


class CatNETCollector(CoverityIssueCollector):

    '''
    A simple collector for Cat.NET reports
    '''

    def process(self, f):
        tree = ET.parse(f)
        root = tree.getroot()
        for e in root.findall('.//Rule'):
            name = e.findtext('Name')
            identifier = e.findtext('Identifier')

            for res in e.findall('.//Result'):
                entry_variable = res.findtext('EntryVariable')
                res_id = res.findtext('Identifier')
                suppressed = res.findtext('Suppressed') != 'false'
                confidence_level = res.findtext('ConfidenceLevel')
                problem = res.findtext('ProblemDescription').replace('\n','').replace('\t',' ')

                msg = self.create_issue(
                    checker='Cat.NET',
                    subcategory=identifier,
                    description=problem,

                    tag=name,
                    extra=res_id
                )

                for trans in res.find('./Transformations'):
                    line = trans.get('line')
                    filename = trans.get('file')
                    tag = trans.findtext('StatementType')

                    # Should this be findText('Method')?
                    method = trans.findtext('StatementMethod')

                    var_in = trans.findtext('InputVariable')
                    var_ain = trans.findtext('ActualInputVariable')
                    var_out = trans.findtext('OutputVariable')

                    if var_in and var_ain and var_in != var_ain:
                        var_in = ' from %s (aka %s)' % (var_ain, var_in)
                    elif var_in:
                        var_in = ' from '+var_in
                    else:
                        var_in = ''

                    description = '%s%s to %s' % (tag, var_in, var_out)

                    try:
                        msg.add_location(line, filename, description, method=method, tag=tag)
                    except AttributeError:
                        for n in ('line','filename','description','method','tag'):
                            print n.upper(), locals()[n]
                        raise

                if confidence_level != 'Low' and not suppressed:
                    # The first loc is going to be treated as the main event,
                    # so let's set that event's description to None so that
                    # it will get the long description associated with the
                    # ProblemDescription field.
                    msg.main_event = -1 
                    msg._locs[msg.main_event].description = None
                    msg.function = msg._locs[msg.main_event].method

                    self.add_issue(msg) 

if __name__ == '__main__':
    import sys
    opts = get_opts('catnet_import.py', sys.argv)
    print CatNETCollector(**opts).run(sys.argv[-1])

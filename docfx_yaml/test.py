# -*- coding: UTF-8 -*-
import yaml
import re

def resolve_xref_type(reference):
    ''' Convert an aggregated type into markdown string with xref tag.
        e.g. input: 'list[azure.core.Model]' -> output: '<xref:list>[<xref:azure.core.Model>]'
    '''
    xref = ''
    http_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    if reference.get('spec.python', None):
        specList = reference['spec.python']
        filterList = list(filter(lambda x: x.get('uid', None), specList))
        d = {}
        for i, item in enumerate(filterList):
            if re.match(http_pattern, item.get('uid')):
                d[item.get('uid')] = True
                d[filterList[i-1].get('uid')] = True
            else:
                d[item.get('uid')] = False

        for i, item in enumerate(specList):
            if item.get('uid', None) and d[item.get('uid')]:
                xref += item["uid"]
            elif item.get('uid', None):
                if xref_pattern.search(item['uid']):
                    xref += item['name']
                else:
                    xref += f'<xref:{item["uid"]}>'
            else:
                xref += item['name']
    else:
        xref += f'<xref:{reference["uid"]}>'

    return xref

def resolve_type(data_type):
        # Remove @ ~ and \n for cross reference in parameter/return value type to apply to docfx correctly
        data_type = re.sub('[@~\n]', '', data_type)

        # Add references for docfx to resolve ref if type contains TYPE_SEP_PATTERN
        _spec_list = []
        _spec_fullnames = re.split(TYPE_SEP_PATTERN, data_type)

        _added_reference = {}
        if len(_spec_fullnames) > 1:
            _added_reference_name = ''
            for _spec_fullname in _spec_fullnames:
                if _spec_fullname != '':
                    _spec = {}
                    _spec['name'] = _spec_fullname.split('.')[-1]
                    _spec['fullName'] = _spec_fullname
                    if re.match(TYPE_SEP_PATTERN, _spec_fullname) is None:
                        _spec['uid'] = _spec_fullname
                    _spec_list.append(_spec)
                    _added_reference_name += _spec['name']

            _added_reference = {
                'uid': data_type,
                'name': _added_reference_name,
                'fullName': data_type,
                'spec.python': _spec_list
            }

        return data_type, _added_reference

summary = u' An object in the form "{activityId: *id of message to delete*,conversation: { id: *id of Slack\nchannel*}}".\n'
obj = {
    'value': summary
}

summary = "Recognizes the user's input.\n\n\n > [!NOTE]\n > When overridden in a derived\
    \ class, attempts to recognize the user\u2019s input.\n >"

summary = summary.replace('\u2019', "'")

exc = '<xref:botframework.connector.models.ErrorResponseException>'

exceptions = exc[6:-1]

PARAMETER_TYPE = "[(]((?:.|\n)*)[)]"
_first_part_ret_data = '** asdfasf (aaaaa or\n bbb) - dsc'
_type_pattern = re.compile(PARAMETER_TYPE, re.DOTALL)

xref_pattern = re.compile(r'<\s*xref\s*:\s*[\w\.]+\s*>')

#print(xref_pattern.search('class:: <xref:str>'))

TYPE_SEP_PATTERN = '(\[|\]|, |\(|\))'

data_type = 'list[<xref:azure.ai.formrecognizer.FormField>]'

_type, _added_reference = resolve_type( data_type)
if _added_reference:
    _type = resolve_xref_type(_added_reference)

print(_type)


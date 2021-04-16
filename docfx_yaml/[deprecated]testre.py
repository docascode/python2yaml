import re
import yaml
import json

PARAMETER_NAME = "[*][*](.*?)[*][*]"
PARAMETER_TYPE = "[(](.*)[)]"
PARAMETER_DESCRIPTION = "[–][ ](.*)"
TYPE_SEP_PATTERN = '(\[|\]|, |\(|\))'


string = "**init_arg1** ([float](https://docs.python.org/3.6/library/functions.html#float)) – Parameter init_arg1 from class docstring.\n"
# string2 = '**init_arg2** ([list](https://docs.python.org/3.6/library/stdtypes.html#list)*[*[int](https://docs.python.org/3.6/library/functions.html#int)*]* \n float) – Parameter init_arg2 from class docstring.\n'
string2 = '**init_arg2** (int \n\nfloat) – Parameter init_arg2 from class docstring.\n'

arg_name = re.compile(PARAMETER_NAME)
arg_type = re.compile(PARAMETER_TYPE, re.M)
description = re.compile(PARAMETER_DESCRIPTION)

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


# print(re.findall(re.compile(PARAMETER_NAME), string))
data = {
    'parameters': [],
    'variables': [],
    'exceptions': [],
    'return': {},
    'references': [],
}
ret = re.findall(arg_type, string2)
print(ret)

for returntype in re.split('[ \n]or[ \n]', ret):
    returntype, _added_reference = resolve_type(returntype)
    if _added_reference:
        if len(data['references']) == 0:
            data['references'].append(_added_reference)
        elif any(r['uid'] != _added_reference['uid'] for r in data['references']):
            data['references'].append(_added_reference)

    data['return'].setdefault('type', []).append(returntype)


print(json.dumps(data, indent = 2, sort_keys=True))
# print(re.findall(description, string))

# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml as yml
from yaml import safe_dump as dump
from functools import partial

xref_pattern = re.compile(r'<\s*xref\s*:\s*[\w\.]+\s*>')


def list_yaml_files(root):
    paths = []
    for subdir, dirs, files in os.walk(root):
        for file in files:
            if file.lower().endswith(".yml"):
                paths.append(os.path.join(subdir, file))

    return paths


def read_yaml(yaml_file_path):
    ''' Read the content of a yaml file if exists and deserialize it into python dict object.

    :param yaml_file_path: Path of the yaml file.
    '''
    if os.path.exists(yaml_file_path):
        with open(yaml_file_path, 'r') as f:
            return yml.load(f.read(), Loader=yml.BaseLoader)
    else:
        print(f'[Error] No such file: {yaml_file_path}.', file=sys.stderr)


def write_yaml(obj, path, mime):
    ''' Write the SDP styled object to a yaml file.

    :param obj: The object in SDP style.
    :param path: Path of the yaml file you would like to write.
    :param mime: Yaml mime type. e.g. PythonClass
    '''
    yaml_mime = f'### YamlMime:{mime}\n'
    yaml_content = yml.dump(obj, default_flow_style=False,
                            indent=2, sort_keys=False)
    with open(path, 'w') as f:
        f.write(yaml_mime + yaml_content)


def parse_references(references):
    ''' Parse references in yaml file and return a dict for query
    '''
    record = {}

    for ref in references:
        record[ref['uid']] = resolve_type(ref)

    return record


def resolve_type(reference):
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
                xref += f'<xref:{item["uid"]}>'
            else:
                xref += item['name']
    else:
        xref += f'<xref:{reference["uid"]}>'

    return xref


def remove_empty_values(dictionary):
    ''' Clear empty values in dictionary. Following values will be regarded as empty:
        empty collections: [], {}, (), set() ...
        zero value: 0
        false boolean: False
        empty string: ''
        none value: None
    '''
    return {k: v for k, v in dictionary.items() if v}


def convert_member(obj, reference_mapping):
    convert_parameter_partial = partial(
        convert_parameter, reference_mapping=reference_mapping)

    if obj:
        member_object = {
            'uid': obj.get('uid', None),
            'name': obj.get('fullName', '').split('.')[-1],
            'summary': obj.get('summary', None),
            'signature': obj.get('syntax', {}).get('content', None),
            'parameters': list(map(convert_parameter_partial, obj.get('syntax', {}).get('parameters', []))),
            'return': convert_return(obj.get('syntax', {}).get('return', {}), reference_mapping),
            'exceptions': obj.get('exceptions', None),
            'examples': obj.get('example', None),
            'seeAlsoContent': obj.get('seealsoContent', None),
            'remarks': obj.get('remarks', None)
        }

        return remove_empty_values(member_object)
    else:
        return {}


def convert_type(type_string):
    ''' Judge whether a type value is xref string, if so, return as it is, if not, convert it into xref string.
    '''
    if type_string and xref_pattern.search(type_string):
        return type_string
    else:
        return f'<xref:{type_string}>'


def convert_types(obj, reference_mapping):
    if obj and isinstance(obj, list):
        return list(map(lambda x: reference_mapping.get(x) if reference_mapping.get(x, None) else convert_type(x), obj))


def convert_return(obj, reference_mapping):
    if obj:
        return_object = {
            'description': obj.get('description', None),
            'types': convert_types(obj.get('type', []), reference_mapping)
        }

        return remove_empty_values(return_object)
    else:
        return {}


def convert_parameter(obj, reference_mapping):
    if obj:
        parameter_object = {
            'name': obj.get('id', None),
            'description': obj.get('description', None),
            'isRequired': str(obj.get('isRequired', '')).lower() == 'true',
            'defaultValue': obj.get('defaultValue', None),
            'types': convert_types(obj.get('type', []), reference_mapping)
        }

        return remove_empty_values(parameter_object)
    else:
        return {}


def get_constructor_and_variables(syntax_object, reference_mapping):
    convert_parameter_partial = partial(
        convert_parameter, reference_mapping=reference_mapping)
    convert_variable_partial = partial(
        convert_variable, reference_mapping=reference_mapping)

    if syntax_object:
        constructor_object = {
            'syntax': syntax_object.get('content', None),
            'parameters': list(map(convert_parameter_partial, syntax_object.get('parameters', [])))
        }

        return remove_empty_values(constructor_object), list(map(convert_variable_partial, syntax_object.get('variables', [])))
    else:
        return {}, []


def convert_variable(obj, reference_mapping):
    if obj:
        variable_object = {
            'description': obj.get('description', None),
            'name': obj.get('id', None),
            'types': convert_types(obj.get('type', []), reference_mapping)
        }

        return remove_empty_values(variable_object)
    else:
        return {}

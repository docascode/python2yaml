# -*- coding: utf-8 -*-
import os
import yaml as yml
from functools import partial
from common import remove_empty_values, parse_references, convert_member, convert_parameter, convert_types, get_constructor_and_variables, convert_variable


def convert_class(obj):
    record = {}
    reference_mapping = {}
    old_class_object = {}

    for item in obj:
        record[item['uid']] = item
        if item['type'] == 'class':
            old_class_object = item

    convert_member_partial = partial(
        convert_member, reference_mapping=reference_mapping)

    new_class_object = {
        'uid': old_class_object.get('uid', None),
        'name': old_class_object.get('name', None),
        'fullName': old_class_object.get('fullName', None),
        'module': old_class_object.get('module', None),
        'inheritances': list(map(lambda x: x.get('type', None), old_class_object.get('inheritance', []))),
        'summary': old_class_object.get('summary', None),
        'constructor': None,
        'variables': None,
        'remarks': old_class_object.get('remarks', None),
        'examples': old_class_object.get('example', None),
        'methods': None,
        'attributes': None,
        'metadata': None
    }

    constructor, variables = get_constructor_and_variables(
        old_class_object.get('syntax', {}), reference_mapping)

    new_class_object['constructor'] = constructor
    new_class_object['variables'] = variables

    children = old_class_object.get('children', [])
    children_objects = list(map(lambda x: record.get(x), children))
    methods = list(filter(lambda x: x.get('type') == 'method', children_objects))
    attributes = list(filter(lambda x: x.get('type') =='attribute', children_objects))

    new_class_object['methods'] = list(map(convert_member_partial, methods))
    new_class_object['attributes'] = list(map(convert_member_partial, attributes))

    print("class: " + new_class_object['uid'])
    return remove_empty_values(new_class_object)

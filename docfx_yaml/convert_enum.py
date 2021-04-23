# -*- coding: utf-8 -*-
from common import remove_empty_values, parse_references, get_constructor_and_variables, convert_variable


def convert_enum(obj):
    ''' Convert the Enum yaml object to a SDP style object.

    :param obj: The object is generated from the Enum yaml file
    '''
    record = {}
    reference_mapping = {}
    old_enum_object = {}

    for item in obj:
        record[item['uid']] = item
        if item['type'] == 'enum':
            old_enum_object = item

    new_enum_object = {
        'uid': old_enum_object.get('uid', None),
        'name': old_enum_object.get('name', None),
        'fullName': old_enum_object.get('fullName', None),
        'summary': old_enum_object.get('summary', None),
        'module': old_enum_object.get('module', None),
        'remarks': old_enum_object.get('remarks', None),
        'constructor': None,
        'variables': None,
        'inheritances': list(map(lambda x: x.get('type', None), old_enum_object.get('inheritance', []))),
        'fields': None,
        'metadata': None
    }

    constructor, variables = get_constructor_and_variables(
        old_enum_object.get('syntax', {}), reference_mapping)

    new_enum_object['constructor'] = constructor
    new_enum_object['variables'] = variables

    children = old_enum_object.get('children', [])
    children_objects = list(map(lambda x: record.get(x), children))
    fields = list(filter(lambda x: x.get('type') ==
                  'attribute', children_objects))

    new_enum_object['fields'] = list(map(convert_fields, fields))

    print("enum: " + new_enum_object['uid'])
    return remove_empty_values(new_enum_object)


def convert_fields(obj):
    if obj and obj.get('uid', []):
        fields_object = {
            'name': obj.get('name', None),
            'uid': obj.get('uid', None)
        }

        return remove_empty_values(fields_object)
    else:
        return {}

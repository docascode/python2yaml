# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re

from docutils import nodes
from sphinx import addnodes
from sphinx.addnodes import desc, desc_signature
from sphinx.util.docfields import _is_single_paragraph

from nodes import remarks

TYPE_SEP_PATTERN = '(\[|\]|, |\(|\))'
PARAMETER_NAME = "[*][*](.*?)[*][*]"
PARAMETER_TYPE = "[(]((?:.|\n)*)[)]"


def translator(app, docname, doctree):

    transform_node = app.docfx_transform_node

    def make_param(_id, _description, _type=None, _required=None):
        ret = {}
        if _id:
            ret['id'] = _id.strip(" \n\r\r")
        if _description:
            ret['description'] = _description.strip(" \n\r\r")
        if _type:
            ret['type'] = _type

        if _required is not None:
                ret['isRequired'] = _required

        return ret

    def transform_para(para_field):
        if isinstance(para_field, nodes.paragraph):
            return transform_node(para_field)
        else:
            return para_field.astext()

    def type_mapping(type_name):
        mapping = {
            "staticmethod": "method",
            "classmethod": "method",
            "exception": "class",
        }

        return mapping[type_name] if type_name in mapping else type_name

    def _get_desc_data(node):
        assert node.tagname == 'desc'
        if node.attributes['domain'] != 'py':
            print(
                'Skipping Domain Object (%s)' % node.attributes['domain']
            )
            return None, None

        try:
            module = node[0].attributes['module']
            full_name = node[0].attributes['fullname']
        except KeyError as e:
            print(
                "[docfx_yaml] There maybe some syntax error in docstring near: " + node.astext())
            raise e

        uid = '{module}.{full_name}'.format(module=module, full_name=full_name)
        return uid

    def _is_desc_of_enum_class(node):
        assert node.tagname == 'desc_content'
        if node[0] and node[0].tagname == 'paragraph' and node[0].astext() == 'Bases: enum.Enum':
            return True

        return False

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
                    xref += f'<xref:{item["uid"]}>'
                else:
                    xref += item['name']
        else:
            xref += f'<xref:{reference["uid"]}>'

        return xref

    def parse_parameter(ret_data, fieldtype):
        _id = None
        _description = None
        _type = None
        _type_list = []
        
        hyphen_index = ret_data.astext().find('–')
        parameter_definition_part = ret_data.astext()[:hyphen_index]
        description_part_index = transform_node(ret_data).find('–')
        _description = transform_node(ret_data)[description_part_index+1 : ]

        if parameter_definition_part.find('(') >= 0:
            _id = parameter_definition_part[: parameter_definition_part.find('(')]
            _type_pattern = re.compile(PARAMETER_TYPE, re.DOTALL)
            if len(_type_pattern.findall(parameter_definition_part)) > 0:
                _types = _type_pattern.findall(parameter_definition_part)[0].replace('*', '')
                if _types:
                    for _type in re.split('[ \n]or[ \n]', _types):
                        _type, _added_reference = resolve_type( _type)
                        if _added_reference:
                            _type = resolve_xref_type(_added_reference)
                        _type_list.append(_type)
        else:
            _id = parameter_definition_part
        
        _data = make_param(_id, _description, _type_list, _required=False if fieldtype == 'Keyword' else True)
        return _data

    def _get_full_data(node):
        data = {
            'parameters': [],
            'variables': [],
            'exceptions': [],
            'return': {},
            'references': [],
        }

        for field in node:
            fieldname, fieldbody = field
            try:
                # split into field type and argument
                fieldtype, _ = fieldname.astext().split(None, 1)
            except ValueError:
                # maybe an argument-less field type?
                fieldtype = fieldname.astext()

            # collect the content, trying not to keep unnecessary paragraphs
            if _is_single_paragraph(fieldbody):
                content = fieldbody
            else:
                content = fieldbody.children

            if fieldtype == 'Raises':
                for exception_node in content:
                    exception_ret = transform_node(exception_node)
                    if exception_ret:
                        description_index = exception_ret.find('–')
                        if description_index >= 0:
                            exception_description = exception_ret[description_index+1:].strip(" \n\r\t")
                            exception_type = exception_ret[:description_index-1].strip(" \n\r\t")
                            if exception_type.find('<xref:') >= 0:
                                exception_type = exception_type[6:-1]
                                data['exceptions'].append({
                                    'description': exception_description,
                                    'type': exception_type
                                })
                        else:
                            exception_type = exception_ret.strip(" \n\r\t")
                            if exception_type.find('<xref:') >= 0:
                                exception_type = exception_type[6:-1]
                                data['exceptions'].append({
                                    'type': exception_type
                                })              
            
            if fieldtype == 'Returns':
                returnvalue_ret = transform_node(content[0])
                if returnvalue_ret:
                    data['return']['description'] = returnvalue_ret.strip(" \n\r\t")

            if fieldtype in ['Return']:
                for returntype_node in content:
                    returntype_ret = transform_node(returntype_node)
                    if returntype_ret:
                        for returntype in re.split('[ \n]or[ \n]', returntype_ret):
                            returntype, _added_reference = resolve_type(
                                returntype)
                            data['return'].setdefault('type', []).append(returntype)

            if fieldtype in ['Parameters', 'Variables', 'Keyword']:
                if _is_single_paragraph(fieldbody):
                    ret_data = transform_para(content[0])
                    #_data = parse_parameter(ret_data, fieldtype)
                    _data = parse_parameter(content[0], fieldtype)
                    if fieldtype in ['Parameters', 'Keyword']:
                        data['parameters'].append(_data)
                    else:
                        _data['id'] = _parse_variable_id(content[0].astext())
                        data['variables'].append(_data)
                else:
                    for child in content[0]:
                        ret_data = transform_para(child[0])
                        _data = parse_parameter(child[0], fieldtype)
                        if fieldtype in ['Parameters', 'Keyword']:
                            data['parameters'].append(_data)
                        else:
                            _data['id'] = _parse_variable_id(child.astext())
                            data['variables'].append(_data)

        return data

    def _parse_variable_id(variable_content):
        if variable_content.find('–') >= 0:
            id_part = variable_content[:variable_content.find('–') - 1]
        else:
            id_part = variable_content
        if id_part.find('(') >= 0:
            variable_id = id_part[:id_part.find('(')].strip(' ')
        else:
            variable_id = id_part.strip(' ')
        return variable_id

    def _is_property_node(node):
        try:
            if isinstance(node.parent[0][0], addnodes.desc_annotation):
                ret = node.parent[0][0].astext()
                if (ret.strip(" ") == 'property'):
                    return True
                else:
                    return False
        except Exception:
            return False

    for node in doctree.traverse(addnodes.desc_content):
        summary = []
        data = {}
        uid = _get_desc_data(node.parent)
        if uid == 'format.google.foo.function':
            print('aaa')
        for child in node:
            if isinstance(child, remarks):
                remarks_string = transform_node(child)
                data['remarks'] = remarks_string
            elif isinstance(child, addnodes.desc):
                if child.get('desctype') == 'attribute':
                    # Used for detecting duplicated attributes in intermediate data and merge them
                    attribute_map = {}

                    for item in child:
                        if isinstance(item, desc_signature) and any(isinstance(n, addnodes.desc_annotation) for n in item):
                            # capture attributes data and cache it
                            data.setdefault('added_attribute', [])
                            curuid = item.get('module', '') + \
                                '.' + item.get('fullname', '')

                            if len(curuid) > 0:
                                parent = curuid[:curuid.rfind('.')]
                                name = item.children[0].astext()

                                if curuid in attribute_map:
                                    # ensure the order of docstring attributes and real attributes is fixed
                                    if len(item_ids) == 0:
                                        attribute_map[curuid]['syntax']['content'] += (
                                            ' ' + item.astext())
                                        # concat the description of duplicated nodes
                                    else:
                                        attribute_map[curuid]['syntax']['content'] = item.astext(
                                        ) + ' ' + attribute_map[curuid]['syntax']['content']
                                else:
                                    if _is_desc_of_enum_class(node):
                                        addedData = {
                                            'uid': curuid,
                                            'id': name,
                                            'parent': parent,
                                            'langs': ['python'],
                                            'name': name,
                                            'fullName': curuid,
                                            'type': item.parent.get('desctype'),
                                            'module': item.get('module'),
                                            'syntax': {
                                                'content': item.astext(),
                                                'return': {
                                                    'type': [parent]
                                                }
                                            }
                                        }
                                    else:
                                        addedData = {
                                            'uid': curuid,
                                            'class': parent,
                                            'langs': ['python'],
                                            'name': name,
                                            'fullName': curuid,
                                            'type': 'attribute',
                                            'module': item.get('module'),
                                            'syntax': {
                                                'content': item.astext()
                                            }
                                        }

                                    attribute_map[curuid] = addedData
                            else:
                                raise Exception(
                                    'ids of node: ' + repr(item) + ' is missing.')
                                # no ids and no duplicate or uid can not be generated.
                    if 'added_attribute' in data:
                        # Add attributes data to a temp list
                        data['added_attribute'].extend(attribute_map.values())

                # Don't recurse into child nodes
                continue
            elif isinstance(child, nodes.field_list):
                _data = _get_full_data(child)
                data.update(_data)
            elif isinstance(child, addnodes.seealso):
                data['seealso'] = transform_node(child)
            elif isinstance(child, nodes.admonition) and 'Example' in child[0].astext():
                # Remove the admonition node
                child_copy = child.deepcopy()
                child_copy.pop(0)
                data['example'] = transform_node(child_copy)
            else:
                content = transform_node(child)
                if not content.startswith('Bases: '):
                    summary.append(content)

        if "desctype" in node.parent and node.parent["desctype"] == 'class':
            # Make sure class doesn't have 'exceptions' field.
            data.pop('exceptions', '')

        if summary:
            data['summary'] = '\n'.join(summary)

        # Don't include empty data
        for key, val in data.copy().items():
            if not val:
                del data[key]
        data['type'] = type_mapping(
            node.parent["desctype"]) if "desctype" in node.parent else 'unknown'
        if _is_property_node(node):
            data['type'] = 'attribute'
        if (uid in app.env.docfx_info_uid_types):
            app.env.docfx_info_field_data[uid] = data

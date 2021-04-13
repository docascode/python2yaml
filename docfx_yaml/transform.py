from docutils import nodes
from sphinx.util.docfields import _is_single_paragraph
from sphinx import addnodes
from sphinx.addnodes import desc, desc_signature
from nodes import remarks

def type_mapping(type_name):
    mapping = {
        "staticmethod": "method",
        "classmethod": "method",
        "exception": "class"
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
        full_name = node[0].attributes['fullname'].split('.')[-1]
    except KeyError as e:
        print("[docfx_yaml] There maybe some syntax error in docstring near: " + node.astext())
        raise e

    try:
        uid = node[0].attributes['ids'][0]
    except Exception:
        uid = '{module}.{full_name}'.format(module=module, full_name=full_name)
        print('Non-standard id: %s' % uid)
    return full_name, uid

def _get_full_data(node):
    data = {}
    parent_desc = node.parent.parent
    name, uid = _get_desc_data(parent_desc)

    if not name:
        return

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
            content = fieldbody.children[0].children
        else:
            content = fieldbody.children

        data.setdefault(uid, {})

        if fieldtype == 'Returns':
            for child in content:
                ret_data = child.astext()
                data[uid].setdefault(fieldtype, []).append(ret_data)

        if fieldtype == 'Raises':
            for child in content:
                ret_data = child.astext()
                data[uid].setdefault(fieldtype, []).append(ret_data)

        if fieldtype == 'Parameters':
            for field, node_list in content:
                _id = field
                _description = node_list[0]
    return data

def _is_desc_of_enum_class(node):
    assert node.tagname == 'desc_content'
    if node[0] and node[0].tagname == 'paragraph' and node[0].astext() == 'Bases: enum.Enum':
        return True

    return False

def transform_yaml(app, docname, doctree):
    for node in doctree.traverse(addnodes.desc_content):
        summary = []
        data = {}
        name, uid = _get_desc_data(node.parent)
        for child in node:
            if isinstance(child, remarks):
                remarks_string = app.docfx_transform_node(child)
                data['remarks'] = remarks_string
            elif isinstance(child, addnodes.desc):
                if child.get('desctype') == 'attribute':
                    attribute_map = {} # Used for detecting duplicated attributes in intermediate data and merge them

                    for item in child:
                        if isinstance(item, desc_signature) and any(isinstance(n, addnodes.desc_annotation) for n in item):
                            # capture attributes data and cache it
                            data.setdefault('added_attribute', [])

                            item_ids = item.get('ids', [''])

                            if len(item_ids) == 0: # find a node with no 'ids' attribute
                                curuid = item.get('module', '') + '.' + item.get('fullname', '')
                                # generate its uid by module and fullname
                            else:
                                curuid = item_ids[0]

                            if len(curuid) > 0:
                                parent = curuid[:curuid.rfind('.')]
                                name = item.children[0].astext()

                                if curuid in attribute_map:
                                    if len(item_ids) == 0: # ensure the order of docstring attributes and real attributes is fixed
                                        attribute_map[curuid]['syntax']['content'] += (' ' + item.astext())
                                        # concat the description of duplicated nodes
                                    else:
                                        attribute_map[curuid]['syntax']['content'] = item.astext() + ' ' + attribute_map[curuid]['syntax']['content']
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
                                raise Exception('ids of node: ' + repr(item) + ' is missing.')
                                # no ids and no duplicate or uid can not be generated.
                    if 'added_attribute' in data:
                        data['added_attribute'].extend(attribute_map.values()) # Add attributes data to a temp list

                # Don't recurse into child nodes
                continue
            elif isinstance(child, nodes.field_list):
                print("FIELDLIST")
            elif isinstance(child, addnodes.seealso):
                data['seealso'] = app.docfx_transform_node(child)
            elif isinstance(child, nodes.admonition) and 'Example' in child[0].astext():
                # Remove the admonition node
                child_copy = child.deepcopy()
                child_copy.pop(0)
                data['example'] = app.docfx_transform_node(child_copy)
            else:
                content = app.docfx_transform_node(child)
                if not content.startswith('Bases: '):
                    summary.append(content)
        
        if "desctype" in node.parent and node.parent["desctype"] == 'class':
                data.pop('exceptions', '') # Make sure class doesn't have 'exceptions' field.

        if summary:
            data['summary'] = '\n'.join(summary)
        
        # Don't include empty data
            for key, val in data.copy().items():
                if not val:
                    del data[key]
        data['type'] = type_mapping(node.parent["desctype"]) if "desctype" in node.parent else 'unknown'
        app.env.docfx_info_field_data[uid] = data


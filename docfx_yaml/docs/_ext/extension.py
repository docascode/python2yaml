import os
import inspect
import re

from yaml import safe_dump as dump

from sphinx.util.console import darkgreen, bold
from sphinx.util import ensuredir
from sphinx.errors import ExtensionError
from sphinx.util.nodes import make_refnode
from settings import API_ROOT

from functools import partial
from itertools import zip_longest

METHOD = 'method'
FUNCTION = 'function'
MODULE = 'module'
CLASS = 'class'
EXCEPTION = 'exception'
ATTRIBUTE = 'attribute'
REFMETHOD = 'meth'
REFFUNCTION = 'func'
INITPY = '__init__.py'
REF_PATTERN = ':(py:)?(func|class|meth|mod|ref):`~?[a-zA-Z_\.<> ]*?`'


def build_init(app):
    """
    Set up environment data
    """
    # if not app.config.docfx_yaml_output:
    #     raise ExtensionError('You must configure an docfx_yaml_output setting')

    # This stores YAML object for modules
    app.env.docfx_yaml_modules = {}
    # This stores YAML object for classes
    app.env.docfx_yaml_classes = {}
    # This stores YAML object for functions
    app.env.docfx_yaml_functions = {}
    # This store the data extracted from the info fields
    app.env.docfx_info_field_data = {}
    # This stores signature for functions and methods
    app.env.docfx_signature_funcs_methods = {}
    # This store the uid-type mapping info
    app.env.docfx_info_uid_types = {}

    # remote = getoutput('git remote -v')

    try:
        app.env.docfx_remote = remote.split('\t')[1].split(' ')[0]
    except Exception:
        app.env.docfx_remote = None
    try:
        app.env.docfx_branch = getoutput('git rev-parse --abbrev-ref HEAD').strip()
    except Exception:
        app.env.docfx_branch = None

    try:
        app.env.docfx_root = getoutput('git rev-parse --show-toplevel').strip()
    except Exception:
        app.env.docfx_root = None

    # patch_docfields(app)

    # app.docfx_transform_node = partial(transform_node, app)
    # app.docfx_transform_string = partial(transform_string, app)

def _fullname(obj):
    """
    Get the fullname from a Python object
    """
    return obj.__module__ + "." + obj.__name__

def process_docstring(app, _type, name, obj, options, lines):
    """
    This function takes the docstring and indexes it into memory.
    """
    # Use exception as class

    if _type == EXCEPTION:
        _type = CLASS

    cls, module = _get_cls_module(_type, name)
    if not module:
        print('Unknown Type: %s' % _type)
        return None

    datam = _create_datam(app, cls, module, name, _type, obj, lines)

    if _type == MODULE:
        if module not in app.env.docfx_yaml_modules:
            app.env.docfx_yaml_modules[module] = [datam]
        else:
            app.env.docfx_yaml_modules[module].append(datam)

    if _type == CLASS:
        if cls not in app.env.docfx_yaml_classes:
            app.env.docfx_yaml_classes[cls] = [datam]
        else:
            app.env.docfx_yaml_classes[cls].append(datam)

    if _type == FUNCTION and app.config.autodoc_functions:
        if datam['uid'] is None:
            raise ValueError("Issue with {0} (name={1})".format(datam, name))
        if cls is None:
            cls = name
        if cls is None:
            raise ValueError("cls is None for name='{1}' {0}".format(datam, name))
        if cls not in app.env.docfx_yaml_functions:
            app.env.docfx_yaml_functions[cls] = [datam]
        else:
            app.env.docfx_yaml_functions[cls].append(datam)

    insert_inheritance(app, _type, obj, datam)
    insert_children_on_module(app, _type, datam)
    insert_children_on_class(app, _type, datam)
    insert_children_on_function(app, _type, datam)

    app.env.docfx_info_uid_types[datam['uid']] = _type

def _get_cls_module(_type, name):
    """
    Get the class and module name for an object

    .. _sending:

    Foo

    """
    cls = None
    if _type in [FUNCTION, EXCEPTION]:
        module = '.'.join(name.split('.')[:-1])
    elif _type in [METHOD, ATTRIBUTE]:
        cls = '.'.join(name.split('.')[:-1])
        module = '.'.join(name.split('.')[:-2])
    elif _type in [CLASS]:
        cls = name
        module = '.'.join(name.split('.')[:-1])
    elif _type in [MODULE]:
        module = name
    else:
        return (None, None)
    return (cls, module)

def _create_datam(app, cls, module, name, _type, obj, lines=None):
    """
    Build the data structure for an autodoc class
    """

    def _update_friendly_package_name(path):
        package_name_index = path.find(os.sep)
        package_name = path[:package_name_index]
        if len(package_name) > 0:
            try:
                for name in namespace_package_dict:
                    if re.match(name, package_name) is not None:
                        package_name = namespace_package_dict[name]
                        path = os.path.join(package_name, path[package_name_index + 1:])
                        return path

            except NameError:
                pass

        return path


    if lines is None:
        lines = []
    short_name = name.split('.')[-1]
    args = []
    try:
        if _type in [METHOD, FUNCTION]:
            argspec = inspect.getargspec(obj) # noqa
            for arg in argspec.args:
                args.append({'id': arg})
            if argspec.defaults:
                for count, default in enumerate(argspec.defaults):
                    cut_count = len(argspec.defaults)
                    # Only add defaultValue when str(default) doesn't contain object address string(object at 0x)
                    # inspect.getargspec method will return wrong defaults which contain object address for some default values, like sys.stdout
                    # Match the defaults with the count
                    if 'object at 0x' not in str(default):
                        args[len(args) - cut_count + count]['defaultValue'] = str(default)
    except Exception:
        print("Can't get argspec for {}: {}".format(type(obj), name))

    if name in app.env.docfx_signature_funcs_methods:
        sig = app.env.docfx_signature_funcs_methods[name]
    else:
        sig = None

    try:
        full_path = inspect.getsourcefile(obj)
        if full_path is None: # Meet a .pyd file
            raise TypeError()
        # Sub git repo path
        path = full_path.replace(app.env.docfx_root, '')
        # Support global file imports, if it's installed already
        import_path = os.path.dirname(inspect.getfile(os))
        path = path.replace(os.path.join(import_path, 'site-packages'), '')
        path = path.replace(import_path, '')

        # Make relative
        path = path.replace(os.sep, '', 1)
        start_line = inspect.getsourcelines(obj)[1]

        path = _update_friendly_package_name(path)

        # Get folder name from conf.py
        path = os.path.join(app.config.folder, path)

        # append relative path defined in conf.py (in case of "binding python" project)
        try:
            source_prefix  # does source_prefix exist in the current namespace
            path = source_prefix + path
        except NameError:
            pass

    except (TypeError, OSError):
        print("Can't inspect type {}: {}".format(type(obj), name))
        path = None
        start_line = None

    datam = {
        'module': module,
        'uid': name,
        'type': _type,
        'name': short_name,
        'fullName': name,
        'source': {
            'remote': {
                'path': path,
                'branch': app.env.docfx_branch,
                'repo': app.env.docfx_remote,
            },
            'id': short_name,
            'path': path,
            'startLine': start_line,
        },
        'langs': ['python'],
    }

    # Only add summary to parts of the code that we don't get it from the monkeypatch
    if _type == MODULE:
        pass
        # lines = _resolve_reference_in_module_summary(lines)
        # summary = app.docfx_transform_string('\n'.join(_refact_example_in_module_summary(lines)))
        # if summary:
        #     datam['summary'] = summary.strip(" \n\r\r")

    if args or sig:
        datam['syntax'] = {}
        if args:
            datam['syntax']['parameters'] = args
        if sig:
            datam['syntax']['content'] = sig
    if cls:
        datam[CLASS] = cls
    if _type in [CLASS, MODULE]:
        datam['children'] = []
        datam['references'] = []

    if _type in [FUNCTION, METHOD]:
        datam['name'] = app.env.docfx_signature_funcs_methods.get(name, datam['name'])

    return datam

def insert_inheritance(app, _type, obj, datam):

    def collect_inheritance(base, to_add):
        for new_base in base.__bases__:
            new_add = {'type': _fullname(new_base)}
            collect_inheritance(new_base, new_add)
            if 'inheritance' not in to_add:
                to_add['inheritance'] = []
            to_add['inheritance'].append(new_add)

    if hasattr(obj, '__bases__'):
        if 'inheritance' not in datam:
            datam['inheritance'] = []
        for base in obj.__bases__:
            to_add = {'type': _fullname(base)}
            collect_inheritance(base, to_add)
            datam['inheritance'].append(to_add)


def insert_children_on_module(app, _type, datam):
    """
    Insert children of a specific module
    """

    if MODULE not in datam or datam[MODULE] not in app.env.docfx_yaml_modules:
        return
    insert_module = app.env.docfx_yaml_modules[datam[MODULE]]
    # Find the module which the datam belongs to
    for obj in insert_module:
        # Add standardlone function to global class
        if _type in [FUNCTION] and \
                obj['type'] == MODULE and \
                obj[MODULE] == datam[MODULE]:
            obj['children'].append(datam['uid'])

            # If it is a function, add this to its module. No need for class and module since this is
            # done before calling this function.
            insert_module.append(datam)

            # obj['references'].append(_create_reference(datam, parent=obj['uid']))
            break
        # Add classes & exceptions to module
        if _type in [CLASS, EXCEPTION] and \
                obj['type'] == MODULE and \
                obj[MODULE] == datam[MODULE]:
            obj['children'].append(datam['uid'])
            # obj['references'].append(_create_reference(datam, parent=obj['uid']))
            break

    if _type in [MODULE]: # Make sure datam is a module.
        # Add this module(datam) to parent module node
        if datam[MODULE].count('.') >= 1:
            parent_module_name = '.'.join(datam[MODULE].split('.')[:-1])

            if parent_module_name not in app.env.docfx_yaml_modules:
                return

            insert_module = app.env.docfx_yaml_modules[parent_module_name]

            for obj in insert_module:
                if obj['type'] == MODULE and obj[MODULE] == parent_module_name:
                    obj['children'].append(datam['uid'])
                    # obj['references'].append(_create_reference(datam, parent=obj['uid']))
                    break

        # Add datam's children modules to it. Based on Python's passing by reference.
        # If passing by reference would be changed in python's future release.
        # Time complex: O(N^2)
        for module, module_contents in app.env.docfx_yaml_modules.items():
            if module != datam['uid'] and \
                    module[:module.rfind('.')] == datam['uid']: # Current module is submodule/subpackage of datam
                for obj in module_contents: # Traverse module's contents to find the module itself.
                    if obj['type'] == MODULE and obj['uid'] == module:
                        datam['children'].append(module)
                        # datam['references'].append(_create_reference(obj, parent=module))
                        break


def insert_children_on_class(app, _type, datam):
    """
    Insert children of a specific class
    """
    if CLASS not in datam:
        return

    insert_class = app.env.docfx_yaml_classes[datam[CLASS]]
    # Find the class which the datam belongs to
    for obj in insert_class:
        if obj['type'] != CLASS:
            continue
        # Add methods & attributes to class
        if _type in [METHOD, ATTRIBUTE] and \
                obj[CLASS] == datam[CLASS]:
            obj['children'].append(datam['uid'])
            # obj['references'].append(_create_reference(datam, parent=obj['uid']))
            insert_class.append(datam)


def insert_children_on_function(app, _type, datam):
    """
    Insert children of a specific class
    """
    if FUNCTION not in datam:
        return

    insert_functions = app.env.docfx_yaml_functions[datam[FUNCTION]]
    insert_functions.append(datam)

def build_finished(app, exception):
    """
    Output YAML on the file system.
    """
    def find_node_in_toc_tree(toc_yaml, to_add_node):
        for module in toc_yaml:
            if module['name'] == to_add_node:
                return module

            if 'items' in module:
                items = module['items']
                found_module = find_node_in_toc_tree(items, to_add_node)
                if found_module != None:
                    return found_module

        return None

    def convert_module_to_package_if_needed(obj):
        if 'source' in obj and 'path' in obj['source'] and obj['source']['path']:
            if obj['source']['path'].endswith(INITPY):
                obj['type'] = 'package'
                return

        for child_uid in obj['children']:
            if child_uid in app.env.docfx_info_uid_types:
                child_uid_type = app.env.docfx_info_uid_types[child_uid]

                if child_uid_type == MODULE:
                    obj['type'] = 'package'
                    return


    normalized_outdir = os.path.normpath(os.path.join(
        app.builder.outdir,  # Output Directory for Builder
        API_ROOT,
    ))
    ensuredir(normalized_outdir)

    toc_yaml = []
    # Used to record filenames dumped to avoid confliction
    # caused by Windows case insensitive file system
    file_name_set = set()

    # Order matters here, we need modules before lower level classes,
    # so that we can make sure to inject the TOC properly
    for data_set in (app.env.docfx_yaml_modules,
                     app.env.docfx_yaml_classes, 
                     app.env.docfx_yaml_functions):  # noqa

        for uid, yaml_data in iter(sorted(data_set.items())):
            if not uid:
                # Skip objects without a module
                continue

            references = []

            # Merge module data with class data
            for obj in yaml_data:
                pass

            # Output file
            if uid.lower() in file_name_set:
                filename = uid + "(%s)" % app.env.docfx_info_uid_types[uid]
            else:
                filename = uid

            out_file = os.path.join(normalized_outdir, '%s.yml' % filename)
            ensuredir(os.path.dirname(out_file))
            if app.verbosity >= 1:
                app.info(bold('[docfx_yaml] ') + darkgreen('Outputting %s' % filename))

            with open(out_file, 'w') as out_file_obj:
                out_file_obj.write('### YamlMime:UniversalReference\n')
                try:
                    dump(
                        {
                            'items': yaml_data,
                            'references': references,
                            'api_name': [],  # Hack around docfx YAML
                        },
                        out_file_obj,
                        default_flow_style=False
                    )
                except Exception as e:
                    raise ValueError("Unable to dump object\n{0}".format(yaml_data)) from e

            file_name_set.add(filename)

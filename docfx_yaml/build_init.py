# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

try:
    from subprocess import getoutput
except ImportError:
    from commands import getoutput

from functools import partial

from utils import transform_node, transform_string


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

    remote = getoutput('git remote -v')

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

    app.docfx_transform_node = partial(transform_node, app)
    app.docfx_transform_string = partial(transform_string, app)

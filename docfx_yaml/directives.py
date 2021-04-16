# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This module is used to add extra supported directives to sphinx.
"""

from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.parsers.rst import Directive
from docutils import nodes

from nodes import remarks


class RemarksDirective(BaseAdmonition):
    """
    Class to enable remarks directive.
    """
    node_class = remarks

class TodoDirective(Directive):
    """
    Class to ignore todo directive.
    """

    # Enable content in the directive
    has_content = True

    # Directive class must override run function.
    def run(self):
        return_nodes = []

        return return_nodes

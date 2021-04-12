from docutils import nodes
from docutils.io import StringOutput
from docutils.nodes import Node
from io import open
from os import path
from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, os_path
from directives import RemarksDirective, TodoDirective
from nodes import remarks
from extension import build_init
from extension import process_docstring
from extension import build_finished

class YamlBuilder(Builder):
    name = 'yaml'
    format = 'yaml'

    out_suffix = '.yml'
    allow_parallel = False

    current_docname = None

    markdown_http_base = 'https://localhost'

    def init(self):
        self.secnumbers = {}

    def get_outdated_docs(self):
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            targetname = path.join(self.outdir, docname + self.out_suffix)
            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                pass

    def get_target_uri(self, docname: str, typ=None):
        # Returns the target markdown file name
        return f"{docname}.yml"

    def prepare_writing(self, docnames):
        pass

    def write_doc(self, docname, doctree):
        pass

    def finish(self):
        pass

def setup(app):
    app.add_builder(YamlBuilder)
    app.add_node(remarks, html = (remarks.visit_remarks, remarks.depart_remarks))
    app.add_directive('remarks', RemarksDirective)
    app.add_directive('todo', TodoDirective)

    app.connect('builder-inited', build_init)
    app.connect('autodoc-process-docstring', process_docstring)
    app.connect('build-finished', build_finished)

    app.add_config_value('autodoc_functions', False, 'env')
    app.add_config_value('folder', '', 'html')
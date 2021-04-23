# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath('../../../docfx_yaml'))
# sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

source_suffix = '.rst'
master_doc = 'index'
project = u'example'
copyright = u'2021, Microsoft'
author = u'Yan Xie'
version = '0.1'
release = '0.1'
language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'Example Document'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'yaml_builder'
]
intersphinx_mapping = {'python': ('https://docs.python.org/3.6', None)}

# Make Google-style and Numpy-style Example work.
napoleon_use_admonition_for_examples = True

# sphinx.ext.extlinks options
extlinks = {
    'cntk': ('bindings/python/%s', ''),
    'cntktut': ('bindings/python/Tutorials/%s.ipynb', ''),
    'cntkwiki': ('https://docs.microsoft.com/en-us/cognitive-toolkit/%s', 'CNTK Doc - ')
}

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

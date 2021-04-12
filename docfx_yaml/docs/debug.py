import os
import shutil
import unittest
from contextlib import contextmanager
from sphinx.application import Sphinx

@contextmanager
def sphinx_build(test_dir):
    # os.chdir('D:\Github\pythonDemo')

    try:
        app = Sphinx(
            srcdir='docfx_yaml\docs',
            confdir='docfx_yaml\docs',
            outdir='docfx_yaml\docs\_build\yaml',
            doctreedir='docfx_yaml\docs/.doctrees',
            buildername='yaml',
        )
        app.build(force_all=True)
        yield
    finally:
        # shutil.rmtree('_build')
        os.chdir('../..')

if __name__ == '__main__':
    with sphinx_build('example'):
        print('Debug finished.')
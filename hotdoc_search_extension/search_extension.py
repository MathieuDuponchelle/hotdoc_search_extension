import os, shutil

from hotdoc.core.base_extension import BaseExtension
from hotdoc.core.base_formatter import Formatter
from hotdoc_search_extension.create_index import create_index

DESCRIPTION=\
"""
This extension enables client-side full-text search
for html documentation produced by hotdoc.
"""

here = os.path.dirname(__file__)

class SearchExtension(BaseExtension):
    EXTENSION_NAME='search'

    def __init__(self, doc_tool, args):
        BaseExtension.__init__(self, doc_tool, args)
        self.enabled = False
        self.script = os.path.abspath(os.path.join(here, '..', 'javascript',
            'trie.js'))

    def setup(self):
        self.enabled = self.doc_tool.output_format == 'html'

        if not self.enabled:
            return

        Formatter.formatting_page_signal.connect(self.__formatting_page)

    def finalize(self):
        if not self.enabled:
            return

        # This is needed for working xhr
        assets_path = self.doc_tool.get_assets_path()
        exclude_dirs = [os.path.join(assets_path, d) for d in ['assets']]
        dest = os.path.join(assets_path, 'js')

        topdir = os.path.abspath(os.path.join(assets_path, '..'))

        subdirs = next(os.walk(topdir))[1]
        subdirs.append(topdir)

        create_index(self.doc_tool.output, exclude_dirs=exclude_dirs,
                dest=dest)

        for subdir in subdirs:
            if subdir == 'assets':
                continue
            shutil.copyfile(os.path.join(dest, 'search', 'dumped.trie'),
                    os.path.join(topdir, subdir, 'dumped.trie'))

    def __formatting_page(self, formatter, page):
        page.output_attrs['html']['scripts'].add(self.script)

def get_extension_classes():
    return [SearchExtension]

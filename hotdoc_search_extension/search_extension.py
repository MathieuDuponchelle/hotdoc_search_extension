import os, shutil, json

from hotdoc.core.base_extension import BaseExtension
from hotdoc.core.doc_tree import Page
from hotdoc_search_extension.create_index import SearchIndex

DESCRIPTION=\
"""
This extension enables client-side full-text search
for html documentation produced by hotdoc.
"""

here = os.path.dirname(__file__)

def list_html_files(root_dir, exclude_dirs):
    html_files = []
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    return html_files

class SearchExtension(BaseExtension):
    EXTENSION_NAME='search'

    def __init__(self, doc_repo, args):
        BaseExtension.__init__(self, doc_repo, args)
        self.enabled = False
        self.script = os.path.abspath(os.path.join(here, '..', 'javascript',
            'trie.js'))

    def setup(self):
        self.enabled = self.doc_repo.output_format == 'html'
        Page.formatting_signal.connect(self.__formatting_page)

    def finalize(self):
        assets_path = os.path.join(self.doc_repo.output, 'assets')
        dest = os.path.join(assets_path, 'js')

        topdir = os.path.abspath(os.path.join(assets_path, '..'))

        subdirs = next(os.walk(topdir))[1]
        subdirs.append(topdir)

        exclude_dirs = ['assets']
        sources = list_html_files(self.doc_repo.output, exclude_dirs)
        stale, unlisted = self.get_stale_files(sources)

        stale |= unlisted

        if not stale:
            return

        index = SearchIndex(self.doc_repo.output, dest,
                self.doc_repo.get_private_folder())
        index.scan(stale)

        for subdir in subdirs:
            if subdir == 'assets':
                continue
            shutil.copyfile(os.path.join(self.doc_repo.get_private_folder(), 'search.trie'),
                    os.path.join(topdir, subdir, 'dumped.trie'))

    def __formatting_page(self, page, formatter):
        page.output_attrs['html']['scripts'].add(self.script)

def get_extension_classes():
    return [SearchExtension]

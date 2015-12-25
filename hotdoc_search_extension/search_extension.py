from hotdoc.core.base_extension import BaseExtension
from hotdoc_search_extension.create_index import create_index

DESCRIPTION=\
"""
This extension enables client-side full-text search
for html documentation produced by hotdoc.
"""

class SearchExtension(BaseExtension):
    EXTENSION_NAME='search'

    def __init__(self, doc_tool, args):
        BaseExtension.__init__(self, doc_tool, args)

    def finalize(self):
        create_index(self.doc_tool.output)

def get_extension_classes():
    return [SearchExtension]

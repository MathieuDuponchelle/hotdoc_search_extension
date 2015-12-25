from hotdoc.core.base_extension import BaseExtension

DESCRIPTION=\
"""
This extension enables client-side full-text search
for html documentation produced by hotdoc.
"""

class SearchExtension(BaseExtension):
    EXTENSION_NAME='search'

    def __init__(self, doc_tool, args):
        BaseExtension.__init__(self, doc_tool, args)

    def setup(self):
        pass

def get_extension_classes():
    return [SearchExtension]

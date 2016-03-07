# -*- coding: utf-8 -*-
#
# Copyright © 2015,2016 Mathieu Duponchelle <mathieu.duponchelle@opencreed.com>
# Copyright © 2015,2016 Collabora Ltd
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

import sys, os

from trie import Trie

def lookup_transformed(self, word):
    word = word.replace('.', '}')
    word = word.replace('_', '|')
    res = self.lookup(word)
    return res

Trie.lookup_transformed = lookup_transformed

here = os.path.dirname(__file__)
ftrie = Trie.from_file(os.path.join(here, '../demo/dumped.trie'))
print(ftrie.lookup_transformed(sys.argv[1]))

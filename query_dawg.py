import sys

from dawg import Dawg

def lookup_transformed(self, word):
    word = word.replace('.', '}')
    word = word.replace('_', '|')
    res = self.lookup(word)
    return res

Dawg.lookup_transformed = lookup_transformed

fdawg = Dawg.from_file('dumped.dawg')
print(fdawg.lookup_transformed(sys.argv[1]))

import sys

from trie import Trie

def lookup_transformed(self, word):
    word = word.replace('.', '}')
    word = word.replace('_', '|')
    res = self.lookup(word)
    return res

Trie.lookup_transformed = lookup_transformed

ftrie = Trie.from_file('dumped.trie')
print(ftrie.lookup_transformed(sys.argv[1]))

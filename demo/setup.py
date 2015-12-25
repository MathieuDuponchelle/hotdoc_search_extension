import sys, re, os, shutil
from hotdoc_search_extension.trie import Trie

if __name__ == '__main__':

    here = os.path.dirname(__file__)
    shutil.copy(os.path.join(here, '../javascript/trie.js'),
            os.path.join(here, 'trie.js'))

    shutil.copy(os.path.join(here, '../javascript/search.js'),
            os.path.join(here, 'search.js'))

    if os.path.exists(os.path.join(here, 'dumped.trie')):
        print ("All done")
        sys.exit(0)

    trie = Trie()
    word_count = 0
    DICT = '/usr/share/dict/words'

    with open(DICT, 'r') as f:
        words = [w.lower() for w in f.read().split()]

    words.sort()
    for word in words:
        if not re.match(r'^[a-z]+$', word):
            continue

        word_count += 1
        # insert all words, using the reversed version as the data associated with
        # it
        trie.insert(word)
        if (word_count % 100) == 0:
            sys.stderr.write("{0}\r".format(word_count))
            sys.stderr.flush()

    trie.to_file(os.path.join(here, 'dumped.trie'))

    try:
        trie.get_node_by_index(0)
        print ("Error: shouldn't be possible to get node by index in a "
               "non-frozen trie")
        sys.exit(-1)
    except AssertionError:
        pass

    ftrie = Trie.from_file(os.path.join(here, 'dumped.trie'))

    # Can't insert in frozen trie
    try:
        ftrie.insert("palapalapa")
        print ("Error: shouldn't be possible to insert in frozen trie")
        sys.exit(-1)
    except AssertionError:
        pass

    # True
    print (trie.lookup('abaff'))
    # True
    print (ftrie.lookup('abaff'))
    # False
    print (trie.lookup('completenonsense'))
    # False
    print (ftrie.lookup('completenonsense'))
